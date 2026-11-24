"""Redis query cache (300s TTL), optional and failure-tolerant.

If Redis is unreachable the app simply skips caching — a query
never fails because the cache is down.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os

logger = logging.getLogger(__name__)

CACHE_TTL_SECONDS = 300


def _client():
    try:
        import redis

        return redis.Redis.from_url(
            os.environ.get("REDIS_URL", "redis://localhost:6379/0"),
            socket_connect_timeout=2,
            socket_timeout=2,
            decode_responses=True,
        )
    except Exception:
        return None


def cache_key(question: str, top_k: int) -> str:
    digest = hashlib.sha256(f"{question.strip().lower()}|{top_k}".encode()).hexdigest()
    return f"query:{digest}"


def get_cached(question: str, top_k: int):
    client = _client()
    if client is None:
        return None
    try:
        raw = client.get(cache_key(question, top_k))
        return json.loads(raw) if raw else None
    except Exception as exc:
        logger.warning("Redis read failed: %s", exc)
        return None


def set_cached(question: str, top_k: int, payload: dict) -> None:
    client = _client()
    if client is None:
        return
    try:
        client.setex(cache_key(question, top_k), CACHE_TTL_SECONDS, json.dumps(payload))
    except Exception as exc:
        logger.warning("Redis write failed: %s", exc)


def redis_available() -> bool:
    client = _client()
    if client is None:
        return False
    try:
        return bool(client.ping())
    except Exception:
        return False
