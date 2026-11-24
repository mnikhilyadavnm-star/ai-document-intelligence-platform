"""AI Document Intelligence Platform — FastAPI backend.

Working portfolio implementation rebuilt from the resume description:
users upload documents and receive source-grounded answers using
semantic search and RAG.

How it works, with no paid service and no API key required:
- Upload: PDF (.pdf via pypdf) or text (.txt / .md) is extracted,
  split into 500-character chunks (100 overlap), embedded with a
  free local TF-IDF hashing vectorizer (scikit-learn, 384 dims),
  and stored in PostgreSQL with pgvector.
- Query: the question is embedded the same way, pgvector returns
  the nearest chunks by cosine distance, the passages are re-ranked
  with TF-IDF, and an extractive, source-grounded answer is built
  from those passages. Results are cached in Redis for 300s.
- Optional LLM: only if ``LLM_API_KEY`` is set, the retrieved
  passages are sent to an OpenAI-compatible chat endpoint and its
  answer is returned instead; any LLM failure falls back to the
  extractive answer.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import cache
from .chunking import ALLOWED_EXTENSIONS, chunk_text, extract_text
from .database import db_available, get_db, init_db
from .embeddings import embed_text, embed_texts
from .models import Chunk, Document
from .rag import build_extractive_answer, maybe_llm_answer
from .schemas import DocumentOut, QueryRequest, QueryResponse, UploadResponse

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    yield


app = FastAPI(title="AI Document Intelligence Platform", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    """Health check, including database and Redis status."""
    return {
        "status": "ok",
        "database": "ok" if db_available() else "unavailable",
        "redis": "ok" if cache.redis_available() else "unavailable",
    }


@app.post("/documents/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload a document, chunk it, embed it and store it."""
    name = (file.filename or "").lower()
    if not any(name.endswith(ext) for ext in ALLOWED_EXTENSIONS):
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Upload a .pdf, .txt or .md document.",
        )
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    try:
        text = extract_text(file.filename or "document", data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    chunks = chunk_text(text)
    vectors = embed_texts(chunks)
    try:
        doc = Document(
            filename=file.filename or "document",
            content_type=file.content_type or "",
            file_size=len(data),
            chunk_count=len(chunks),
        )
        db.add(doc)
        db.flush()  # assigns doc.id
        for index, (chunk, vector) in enumerate(zip(chunks, vectors)):
            db.add(
                Chunk(
                    document_id=doc.id,
                    chunk_index=index,
                    text=chunk,
                    embedding=vector,
                )
            )
        db.commit()
    except Exception as exc:
        db.rollback()
        logger.exception("Failed to store document: %s", exc)
        raise HTTPException(
            status_code=503,
            detail="Database is unavailable. Start PostgreSQL (docker compose up) and try again.",
        ) from exc
    return UploadResponse(
        id=doc.id,
        filename=doc.filename,
        chunk_count=len(chunks),
        message=f"Uploaded {doc.filename}: {len(chunks)} chunks stored.",
    )


@app.get("/documents", response_model=list[DocumentOut])
def list_documents(db: Session = Depends(get_db)):
    """List uploaded documents, newest first."""
    try:
        docs = db.execute(
            select(Document).order_by(Document.created_at.desc())
        ).scalars().all()
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="Database is unavailable. Start PostgreSQL (docker compose up) and try again.",
        ) from exc
    return docs


@app.get("/documents/{document_id}", response_model=DocumentOut)
def get_document(document_id: int, db: Session = Depends(get_db)):
    doc = db.get(Document, document_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found.")
    return doc


@app.delete("/documents/{document_id}")
def delete_document(document_id: int, db: Session = Depends(get_db)):
    doc = db.get(Document, document_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found.")
    db.delete(doc)
    db.commit()
    return {"message": f"Deleted document {document_id}."}


@app.post("/query", response_model=QueryResponse)
async def query_documents(payload: QueryRequest, db: Session = Depends(get_db)):
    """Ask a question and get a source-grounded answer."""
    question = payload.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question must not be empty.")

    cached = cache.get_cached(question, payload.top_k)
    if cached is not None:
        cached["cached"] = True
        return QueryResponse(**cached)

    # Semantic search in pgvector: nearest chunks by cosine distance.
    try:
        query_vector = embed_text(question)
        rows = db.execute(
            select(Chunk, Document.filename)
            .join(Document, Chunk.document_id == Document.id)
            .order_by(Chunk.embedding.cosine_distance(query_vector))
            .limit(payload.top_k)
        ).all()
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="Database is unavailable. Start PostgreSQL (docker compose up) and try again.",
        ) from exc

    passages = [
        {
            "document_name": filename,
            "chunk_index": chunk.chunk_index,
            "text": chunk.text,
        }
        for chunk, filename in rows
    ]
    # If the best pgvector hit is still unrelated, the extractive
    # answer says so rather than inventing one.
    result = build_extractive_answer(question, passages)
    answer_type = "extractive"
    llm_answer = await maybe_llm_answer(question, result["sources"])
    if llm_answer:
        result["answer"] = llm_answer
        answer_type = "llm"

    response = QueryResponse(
        question=question,
        answer=result["answer"],
        answer_type=answer_type,
        sources=result["sources"],
        cached=False,
    )
    cache.set_cached(question, payload.top_k, response.model_dump(mode="json"))
    return response
