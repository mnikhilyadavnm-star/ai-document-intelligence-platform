"""Tests that run without a database, Redis, or any API key.

Run from the backend directory:
    python -m pytest tests/ -v
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.chunking import chunk_text, extract_text  # noqa: E402
from app.embeddings import (  # noqa: E402
    EMBEDDING_DIM,
    cosine_similarity,
    embed_text,
    tfidf_scores,
)
from app.rag import build_extractive_answer  # noqa: E402


def test_chunking_splits_with_overlap():
    text = "abcdefghij" * 60  # 600 chars
    chunks = chunk_text(text, chunk_size=500, overlap=100)
    assert len(chunks) == 2
    assert len(chunks[0]) == 500
    # Overlap: chunk 2 starts where chunk 1's last 100 chars start.
    assert chunks[1].startswith(chunks[0][-100:])
    # Short text is a single chunk.
    assert chunk_text("hello") == ["hello"]
    assert chunk_text("") == []
    with pytest.raises(ValueError):
        chunk_text("hello", chunk_size=100, overlap=100)


def test_extract_text_txt_and_rejects_binary():
    assert "hello world" in extract_text("notes.txt", b"hello world\nsecond line")
    assert "hello world" in extract_text("notes.md", b"# hello world")
    with pytest.raises(ValueError):
        extract_text("photo.png", b"\x89PNG")


def test_embeddings_are_deterministic_384d_and_normalised():
    a = embed_text("the quick brown fox jumps over the lazy dog")
    b = embed_text("the quick brown fox jumps over the lazy dog")
    assert len(a) == EMBEDDING_DIM
    assert a == b  # deterministic, no fitting step
    import math

    assert math.isclose(sum(v * v for v in a), 1.0, rel_tol=1e-5)
    # Similar texts are closer than unrelated texts.
    similar = embed_text("the quick brown fox runs fast")
    unrelated = embed_text("quantum chromodynamics lattice gauge theory")
    assert cosine_similarity(a, similar) > cosine_similarity(a, unrelated)


def test_tfidf_scores_rank_relevant_passage_first():
    query = "how do I reset my password"
    passages = [
        "The quarterly revenue grew by twelve percent in March.",
        "To reset your password, open Settings, choose Security, then Reset Password.",
    ]
    scores = tfidf_scores(query, passages)
    assert len(scores) == 2
    assert scores[1] > scores[0]


def test_extractive_answer_is_grounded_in_sources():
    passages = [
        {
            "document_name": "guide.txt",
            "chunk_index": 0,
            "text": "To reset your password, open Settings, choose Security, then Reset Password.",
        },
        {
            "document_name": "guide.txt",
            "chunk_index": 1,
            "text": "The office is closed on public holidays.",
        },
    ]
    result = build_extractive_answer("how do I reset my password?", passages)
    assert "reset your password" in result["answer"].lower()
    assert "guide.txt" in result["answer"]
    assert result["sources"][0]["document_name"] == "guide.txt"
    assert all("text" in s for s in result["sources"])


def test_extractive_answer_with_no_passages_says_so():
    result = build_extractive_answer("anything?", [])
    assert result["sources"] == []
    assert "could not find" in result["answer"].lower()


def test_health_endpoint_without_database():
    from fastapi.testclient import TestClient

    from app.main import app

    with TestClient(app) as client:
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"
        # Database is not running in the test env; health must still answer.
        assert resp.json()["database"] in ("ok", "unavailable")
