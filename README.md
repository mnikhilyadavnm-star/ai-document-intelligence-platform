# AI Document Intelligence Platform

> Portfolio documentation and starter skeleton based on the resume description; not the original production code.

## What it does

The AI Document Intelligence Platform is a platform where users upload documents and receive source-grounded answers using semantic search and RAG. It is built with Python, FastAPI, React, PostgreSQL (pgvector), Redis, LLM APIs, Docker, and AWS.

## Tech Stack

| Layer | Technology |
| --- | --- |
| Backend | Python, FastAPI |
| Frontend | React |
| Database / Vector search | PostgreSQL with pgvector |
| Cache / Queue | Redis |
| AI | LLM APIs |
| Containers | Docker |
| Cloud | AWS |

## Architecture Overview

```
Upload -> Chunk / Embed -> PostgreSQL (pgvector) semantic search
       -> RAG with LLM APIs -> Source-grounded answer
```

1. **Upload** — A user uploads a document through the React frontend.
2. **Chunk / Embed** — The backend prepares the document for retrieval.
3. **Semantic search** — PostgreSQL with pgvector is used to find relevant passages.
4. **RAG** — Retrieved passages are provided as context to LLM APIs.
5. **Answer** — The user receives a source-grounded answer, with sources from the uploaded documents.

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
│   ├── app/
│   │   └── main.py
│   └── requirements.txt
└── frontend/
    └── src/
        └── App.jsx
```

## Local Setup with Docker Compose

Prerequisites: Docker and Docker Compose. See [docs/SETUP.md](docs/SETUP.md) for the full steps.

```bash
cp .env.example .env
docker compose up --build
```

Services:

| Service | Port |
| --- | --- |
| Backend (FastAPI) | 8000 |
| Frontend (React) | 3000 |
| PostgreSQL (pgvector) | 5432 |
| Redis | 6379 |

## API Endpoints

The following are a starter API design, not production:

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/documents/upload` | Upload a document (starter stub) |
| `POST` | `/query` | Ask a question and receive a source-grounded answer (starter stub) |
| `GET` | `/documents` | List uploaded documents (starter stub) |
| `GET` | `/health` | Health check |

## Environment Variables

Copy `.env.example` to `.env` and fill in placeholders. Do not commit real keys.

See [.env.example](.env.example).

## How to Run

```bash
# With Docker Compose (recommended for local setup)
docker compose up --build

# Backend only (see docs/SETUP.md)
# Frontend only (see docs/SETUP.md)
```

Open the frontend at `http://localhost:3000` and the backend health check at `http://localhost:8000/health`.

## Roadmap / Limitations

- The endpoints in `backend/app/main.py` are starter stubs that return `501` / TODO responses. Document parsing, chunking, embedding, retrieval, and LLM integration are not implemented in this skeleton.
- The frontend in `frontend/src/App.jsx` is a placeholder UI with upload and ask forms and fetch stubs.
- The Docker Compose services for the backend and frontend are placeholders and will need the application code completed before they run end to end.
- No accuracy, performance, or production-use claims are made in this documentation.

## Author

Nikhil M, Software Engineer. MS in Computer Science, University of Texas at Arlington (2023–2025).
