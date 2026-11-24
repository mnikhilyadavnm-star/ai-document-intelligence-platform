"""AI Document Intelligence Platform — FastAPI starter skeleton.

Portfolio documentation and starter skeleton based on the resume
description; not the original production code.

Users upload documents and receive source-grounded answers using
semantic search and RAG. The endpoints below are starter stubs.
"""

from fastapi import FastAPI, UploadFile

app = FastAPI(title="AI Document Intelligence Platform")


@app.get("/health")
def health_check():
    """Health check."""
    return {"status": "ok"}


@app.post("/documents/upload")
def upload_document(file: UploadFile):
    """Upload a document — starter stub.

    TODO: parse the document, chunk it, embed it, and store it
    in PostgreSQL (pgvector).
    """
    return {"status": "not implemented", "detail": "TODO: implement document upload"}, 501


@app.post("/query")
def query_documents(payload: dict):
    """Ask a question — starter stub.

    TODO: run semantic search in PostgreSQL (pgvector), pass the
    retrieved passages to LLM APIs (RAG), and return a
    source-grounded answer.
    """
    return {"status": "not implemented", "detail": "TODO: implement RAG query"}, 501


@app.get("/documents")
def list_documents():
    """List uploaded documents — starter stub.

    TODO: list documents stored in PostgreSQL.
    """
    return {"status": "not implemented", "detail": "TODO: implement document listing"}, 501
