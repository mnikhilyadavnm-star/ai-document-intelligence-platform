"""Free local embeddings: TF-IDF via scikit-learn, hashed to 384 dims.

No external embedding API and no API key are needed.

Why hashing? A normal ``TfidfVectorizer`` has to be *fitted* on a
corpus, so its vocabulary changes every time a document is added and
old vectors stop being comparable with new ones. A
``HashingVectorizer`` is stateless and deterministic: the same text
always maps to the same 384-dimensional, L2-normalised vector, so a
query embedded today is comparable with a chunk embedded last week.
The 384 dimensions match the common small-embedding size and fit the
``VECTOR(384)`` column in PostgreSQL / pgvector, where cosine
similarity is computed with the ``<=>`` operator.

On top of that, :func:`tfidf_scores` fits a real TF-IDF vectorizer on
just the retrieved passages plus the query at query time. That is used
to re-rank the pgvector candidates, so the final ordering reflects
term importance in the actual retrieved set, not only the hash.
"""

from __future__ import annotations

import numpy as np
from sklearn.feature_extraction.text import HashingVectorizer, TfidfVectorizer

EMBEDDING_DIM = 384

_vectorizer = HashingVectorizer(
    n_features=EMBEDDING_DIM,
    alternate_sign=False,  # keep counts non-negative so cosine works
    norm="l2",
    ngram_range=(1, 2),
    stop_words="english",
)


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed each text as a 384-dim L2-normalised vector."""
    if not texts:
        return []
    matrix = _vectorizer.transform(texts)
    return [[float(v) for v in row] for row in matrix.toarray()]


def embed_text(text: str) -> list[float]:
    """Embed a single text."""
    return embed_texts([text])[0]


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Cosine similarity for two (already L2-normalised) vectors."""
    va = np.asarray(a, dtype=float)
    vb = np.asarray(b, dtype=float)
    denom = float(np.linalg.norm(va) * np.linalg.norm(vb))
    if denom == 0:
        return 0.0
    return float(np.dot(va, vb) / denom)


def tfidf_scores(query: str, passages: list[str]) -> list[float]:
    """TF-IDF cosine similarity between a query and each passage.

    The vectorizer is fitted on the passages plus the query, so this
    is a re-ranking score for an already-retrieved set, not a
    replacement for the pgvector search.
    """
    if not passages:
        return []
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
    try:
        matrix = vectorizer.fit_transform(passages + [query])
    except ValueError:
        # Empty vocabulary (e.g. only stop words): no signal.
        return [0.0] * len(passages)
    query_vec = matrix[-1]
    passage_vecs = matrix[:-1]
    scores = passage_vecs @ query_vec.T
    return [float(v) for v in np.asarray(scores.todense()).ravel()]
