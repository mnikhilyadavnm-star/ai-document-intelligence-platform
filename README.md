# AI Document Intelligence Platform

> Working portfolio implementation rebuilt from the resume description; not the original production code.

## What it does

Users upload documents and receive source-grounded answers using semantic search and RAG. Built with Python, FastAPI, React, PostgreSQL (pgvector), Redis, LLM APIs, Docker, and AWS (as a deployment sketch only — nothing is deployed here).

**No API key is required to run it locally.** By default it uses free local TF-IDF embeddings (scikit-learn, hashed to 384 dimensions) stored in pgvector, and extractive answers built only from the retrieved passages. An LLM is optional: set `LLM_API_KEY` and the retrieved passages are sent to an OpenAI-compatible chat endpoint instead; if the LLM call fails, it falls back to the extractive answer.

## Tech Stack

| Layer | Technology |
| --- | --- |
| Backend | Python, FastAPI |
| Frontend | React + Vite |
| Database / Vector search | PostgreSQL with pgvector (`VECTOR(384)`) |
| Cache | Redis (query results, 300s TTL) |
| AI (default, free) | TF-IDF embeddings (scikit-learn) + extractive RAG |
| AI (optional) | LLM APIs, only if `LLM_API_KEY` is set |
| Containers | Docker |

## How it works

```
Upload -> Extract text (pypdf / UTF-8) -> Chunk (500 chars, 100 overlap)
       -> TF-IDF hash embedding (384 dims) -> PostgreSQL (pgvector)
Query  -> Embed question -> pgvector cosine search (top-k)
       -> TF-IDF re-rank -> Extractive answer + sources (or optional LLM)
       -> Redis cache (300s)
```

1. **Upload** — `POST /documents/upload` accepts `.pdf`, `.txt`, `.md`. Text is extracted, chunked, embedded, and stored with the document in Postgres.
2. **Semantic search** — the question is embedded the same deterministic way, and pgvector returns the nearest chunks by cosine distance.
3. **Answer** — an extractive answer is built from the best passages, naming each source document and chunk. With `LLM_API_KEY` set, an LLM answer grounded in the same passages is used instead.

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for more detail.

## Project Structure

```
.
├── README.md
├── docker-compose.yml
├── .env.example
├── .gitignore
├── docs/
│   ├── ARCHITECTURE.md
│   └── SETUP.md
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app/
│   │   ├── main.py          # FastAPI app: upload, list, query, health
│   │   ├── database.py      # SQLAlchemy + pgvector setup
│   │   ├── models.py        # Document and Chunk (VECTOR(384))
│   │   ├── chunking.py      # PDF/text extraction + 500/100 chunking
│   │   ├── embeddings.py    # TF-IDF hashing embeddings + TF-IDF re-rank
│   │   ├── rag.py           # Extractive answer + optional LLM
│   │   ├── cache.py         # Redis query cache (300s TTL)
│   │   └── schemas.py       # Pydantic schemas
│   └── tests/
│       └── test_api.py
└── frontend/
    ├── Dockerfile
    ├── package.json
    ├── vite.config.js
    ├── index.html
    └── src/
        ├── main.jsx
        ├── App.jsx          # Upload, document list, ask + sources UI
        └── index.css
```

## Run locally with Docker Compose

Prerequisites: Docker and Docker Compose. No API key, no AWS account, no deployment.

```bash
cp .env.example .env
docker compose up --build
```

| Service | Port |
| --- | --- |
| Backend (FastAPI) | 8000 |
| Frontend (React) | 3000 |
| PostgreSQL (pgvector) | 5432 |
| Redis | 6379 |

Open the frontend at `http://localhost:3000` and the backend health check at `http://localhost:8000/health`. Interactive API docs are at `http://localhost:8000/docs`.

Try it: upload a `.txt` or `.pdf`, then ask a question about it. The answer shows the passages it came from, with document name and chunk.

## Run the tests

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m pytest tests/ -v
```

Tests run without a database, Redis, or any API key: chunking, text extraction, deterministic 384-dim embeddings, TF-IDF ranking, extractive answers, and the health endpoint.

## API Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/documents/upload` | Upload `.pdf` / `.txt` / `.md`; returns document id and chunk count |
| `GET` | `/documents` | List uploaded documents |
| `GET` | `/documents/{id}` | Get one document |
| `DELETE` | `/documents/{id}` | Delete a document and its chunks |
| `POST` | `/query` | Ask a question; returns answer, answer type (`extractive` or `llm`), sources, and whether it was cached |
| `GET` | `/health` | Health check, including database and Redis status |

Example:

```bash
curl -F "file=@notes.txt" http://localhost:8000/documents/upload
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "How do I reset my password?", "top_k": 5}'
```

## Environment Variables

Copy `.env.example` to `.env`. Do not commit real keys.

| Variable | Required | Description |
| --- | --- | --- |
| `DATABASE_URL` | No (defaults to the Compose DB) | PostgreSQL connection string |
| `REDIS_URL` | No (defaults to `redis://localhost:6379/0`) | Redis connection string |
| `LLM_API_KEY` | No — leave empty for free local mode | Optional LLM key |
| `LLM_API_BASE_URL` | No | OpenAI-compatible base URL |
| `LLM_MODEL` | No | LLM model name |

## Limitations

- Embeddings are TF-IDF hashed vectors, not neural embeddings — they match on words and word pairs, so they are good for keyword-heavy documents and weaker for paraphrase-heavy questions.
- The default answer is extractive: it quotes and combines the best retrieved sentences rather than writing a new paragraph. That keeps every claim traceable to a source, at the cost of fluency.
- This is a local portfolio implementation. No accuracy, performance, or production-use claims are made, and nothing here deploys to AWS or any cloud.

## Author

Nikhil M, Software Engineer. MS in Computer Science, University of Texas at Arlington (2023–2025).
