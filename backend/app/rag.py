"""Retrieval-augmented generation — extractive by default.

No LLM call is made unless ``LLM_API_KEY`` is set. The default
answer is *extractive*: it is built only from the retrieved passages,
so every sentence in it can be traced to a named document. That is
the source-grounded behaviour the resume describes, without any
paid API.

Optional LLM path: if ``LLM_API_KEY`` is set, the retrieved passages
are sent as context to an OpenAI-compatible chat-completions
endpoint (``LLM_API_BASE_URL`` / ``LLM_MODEL``). Any failure there
falls back to the extractive answer — a query never fails just
because the optional LLM is unavailable.
"""

from __future__ import annotations

import os
import re

from .embeddings import tfidf_scores

SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")


def _sentences(text: str) -> list[str]:
    return [s.strip() for s in SENTENCE_RE.split(text.strip()) if s.strip()]


def _question_words(question: str) -> set[str]:
    return {w.lower() for w in re.findall(r"[a-zA-Z0-9]+", question) if len(w) > 2}


def build_extractive_answer(question: str, passages: list[dict]) -> dict:
    """Build a source-grounded answer from retrieved passages.

    ``passages`` is a list of dicts with ``document_name``,
    ``chunk_index``, ``text`` and optionally ``score``. Returns a
    dict with ``answer`` and ``sources`` (the passages, in rank
    order, with their document name and chunk index).
    """
    if not passages:
        return {
            "answer": (
                "I could not find any relevant passages in your uploaded "
                "documents for that question. Try uploading a document "
                "that covers the topic, or rephrasing the question."
            ),
            "sources": [],
        }

    # Re-rank with TF-IDF over the retrieved set, then keep the order.
    texts = [p["text"] for p in passages]
    scores = tfidf_scores(question, texts)
    ranked = sorted(
        zip(passages, scores), key=lambda pair: pair[1], reverse=True
    )
    ordered = [p for p, _ in ranked]

    words = _question_words(question)
    picked: list[str] = []
    for passage in ordered:
        for sentence in _sentences(passage["text"]):
            if not picked or len(picked) < 3:
                # Prefer sentences sharing a word with the question.
                if words and any(w in sentence.lower() for w in words):
                    picked.append(sentence)
        if len(picked) >= 3:
            break
    if not picked:
        # No sentence shared a word: use the opening sentences of the
        # best passages rather than saying nothing.
        for passage in ordered[:2]:
            picked.extend(_sentences(passage["text"])[:2])
    picked = picked[:4]

    doc_names = []
    for passage in ordered:
        if passage["document_name"] not in doc_names:
            doc_names.append(passage["document_name"])
    answer = (
        "Based on your uploaded documents ("
        + ", ".join(doc_names)
        + "): "
        + " ".join(picked)
    )
    sources = [
        {
            "document_name": p["document_name"],
            "chunk_index": p.get("chunk_index", 0),
            "text": p["text"],
            "score": round(float(s), 4),
        }
        for p, s in ranked
    ]
    return {"answer": answer, "sources": sources}


async def maybe_llm_answer(question: str, passages: list[dict]) -> str | None:
    """Ask the optional LLM for an answer, or return None.

    Returns None when no key is configured, so the caller falls back
    to the extractive answer. Any network / API error also returns
    None instead of raising.
    """
    api_key = os.environ.get("LLM_API_KEY", "").strip()
    if not api_key or not passages:
        return None
    try:
        import httpx

        base_url = os.environ.get(
            "LLM_API_BASE_URL", "https://api.openai.com/v1"
        ).rstrip("/")
        model = os.environ.get("LLM_MODEL", "gpt-4o-mini")
        context = "\n\n".join(
            f"[{p['document_name']} chunk {p.get('chunk_index', 0)}]\n{p['text']}"
            for p in passages
        )
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": [
                        {
                            "role": "system",
                            "content": (
                                "Answer only from the provided passages. "
                                "If the passages do not contain the answer, "
                                "say so. Cite the document name for each fact."
                            ),
                        },
                        {
                            "role": "user",
                            "content": f"Question: {question}\n\nPassages:\n{context}",
                        },
                    ],
                },
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"].strip()
    except Exception:
        return None
