# Architecture

> Working portfolio implementation rebuilt from the resume description; not the original production code.

## Components

| Component | Technology | Role |
| --- | --- | --- |
| Frontend | React + Vite | Upload documents, list them, ask questions, show answer + sources |
| Backend API | Python, FastAPI | Upload / query endpoints, chunking, embedding, retrieval |
| Database / Vector store | PostgreSQL with pgvector | Documents, chunks, and `VECTOR(384)` embeddings in one database |
| Cache | Redis | Query results cached by question hash, 300s TTL |
| AI (default, free) | TF-IDF (scikit-learn) + extractive RAG | Local embeddings and passage-based answers, no API key |
| AI (optional) | LLM APIs | Grounded generation from the same retrieved passages, only if `LLM_API_KEY` is set |
| Containers | Docker | Local development packaging |

## Data Flow

```
User
  |
  v
React frontend
  |
  v
FastAPI backend
  |
  +--> PostgreSQL (pgvector): chunks + 384-dim embeddings, cosine search
  |
  +--> Redis: cached query results (300s)
  |
  +--> LLM APIs (optional): grounded generation from retrieved passages
  |
  v
Source-grounded answer (with document name + chunk for each source)
```

### Upload flow

1. The user uploads a `.pdf`, `.txt`, or `.md` through the React frontend.
2. FastAPI extracts text (pypdf for PDF, UTF-8 for text/Markdown).
3. Text is split into 500-character chunks with 100-character overlap.
4. Each chunk is embedded with a deterministic TF-IDF hashing vectorizer (scikit-learn, 384 dims, L2-normalised).
5. The document and its chunks + embeddings are stored in PostgreSQL in one transaction.

### Query / RAG flow

1. The user submits a question through the frontend.
2. The backend checks Redis for a cached answer for that question (300s TTL).
3. On a miss, the question is embedded the same way and pgvector returns the nearest chunks by cosine distance (`<=>`), top-k (default 5).
4. Retrieved passages are re-ranked with TF-IDF cosine similarity against the question.
5. By default, an extractive answer is built from the best passages — sentences that share words with the question, with the source document and chunk named. If `LLM_API_KEY` is set, the same passages are sent to an OpenAI-compatible chat endpoint and its answer is returned instead; any LLM failure falls back to the extractive answer.
6. The answer is cached in Redis and returned with its sources.

## Why pgvector + Redis

- **PostgreSQL (pgvector):** document data and vector embeddings live in one database, so retrieval is a single ordered query — no separate vector store to run.
- **TF-IDF hashing embeddings:** stateless and deterministic, so a query embedded today is comparable with a chunk embedded earlier. This avoids any paid embedding API while keeping the pgvector search real.
- **Redis:** identical questions within 5 minutes are served from cache instead of re-running the search.

## AWS Deployment Sketch

This is a sketch only — nothing in this repo deploys to AWS:

- **S3** — for storing uploaded documents.
- **EC2 / ECS** — for running the containerised backend and frontend (Docker).
- **RDS PostgreSQL** — for PostgreSQL with pgvector.
- **ElastiCache Redis** — for Redis.

No deployment, availability, or performance claims are made here.
