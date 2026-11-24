"""Database setup: PostgreSQL + pgvector via SQLAlchemy.

``DATABASE_URL`` defaults to the Docker Compose database, so the
app works out of the box with ``docker compose up --build``.
``init_db()`` is best-effort: if Postgres is not reachable yet (for
example when the API is started before the database), it logs a
warning and leaves the app running — ``/health`` then reports the
database as unavailable instead of the whole service crashing.
"""

from __future__ import annotations

import logging
import os

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from .models import Base

logger = logging.getLogger(__name__)

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/ai_docs",
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db() -> bool:
    """Create the pgvector extension and tables. Returns True on success."""
    try:
        with engine.begin() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        Base.metadata.create_all(bind=engine)
        return True
    except Exception as exc:  # Postgres not up yet, or bad DATABASE_URL
        logger.warning("Database init failed (will retry on request): %s", exc)
        return False


def get_db() -> Session:
    """FastAPI dependency: one session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def db_available() -> bool:
    """Cheap liveness check used by /health."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
