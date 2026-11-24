"""Pydantic schemas for the API."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class DocumentOut(BaseModel):
    id: int
    filename: str
    content_type: str
    file_size: int
    chunk_count: int
    created_at: datetime

    model_config = {"from_attributes": True}


class UploadResponse(BaseModel):
    id: int
    filename: str
    chunk_count: int
    message: str


class SourceOut(BaseModel):
    document_name: str
    chunk_index: int
    text: str
    score: float


class QueryRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    top_k: int = Field(default=5, ge=1, le=10)


class QueryResponse(BaseModel):
    question: str
    answer: str
    answer_type: str  # "extractive" or "llm"
    sources: list[SourceOut]
    cached: bool = False
