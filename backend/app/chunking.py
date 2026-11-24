"""Document text extraction and chunking.

Free, local, no external API: PDF text is extracted with pypdf,
plain text / Markdown is decoded as UTF-8. Chunks are 500 characters
with a 100-character overlap by default, so a passage never loses
its surrounding context at a boundary.
"""

from __future__ import annotations

import io

ALLOWED_EXTENSIONS = {".pdf", ".txt", ".md"}
DEFAULT_CHUNK_SIZE = 500
DEFAULT_OVERLAP = 100


def extract_text(filename: str, data: bytes) -> str:
    """Extract plain text from an uploaded file.

    Raises ValueError for unsupported types or empty documents.
    """
    name = (filename or "").lower()
    if name.endswith(".pdf"):
        from pypdf import PdfReader

        reader = PdfReader(io.BytesIO(data))
        parts = []
        for page in reader.pages:
            parts.append(page.extract_text() or "")
        text = "\n".join(parts)
    elif name.endswith((".txt", ".md")):
        text = data.decode("utf-8", errors="replace")
    else:
        raise ValueError(
            "Unsupported file type. Upload a .pdf, .txt or .md document."
        )
    text = " ".join(text.split())
    if not text.strip():
        raise ValueError("Could not extract any text from this document.")
    return text


def chunk_text(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_OVERLAP,
) -> list[str]:
    """Split text into overlapping chunks.

    A chunk is at most ``chunk_size`` characters. Each chunk after the
    first re-uses the last ``overlap`` characters of the previous one,
    so sentences that straddle a boundary still appear whole in at
    least one chunk. Short texts return a single chunk.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be >= 0 and < chunk_size")
    text = text.strip()
    if not text:
        return []
    if len(text) <= chunk_size:
        return [text]
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        if end >= len(text):
            break
        start = end - overlap
    return chunks
