# Architecture

> Portfolio documentation and starter skeleton based on the resume description; not the original production code.

## Components

| Component | Technology | Role |
| --- | --- | --- |
| Frontend | React | Upload documents and ask questions |
| Backend API | Python, FastAPI | Receives uploads and queries, coordinates retrieval and generation |
| Database / Vector store | PostgreSQL with pgvector | Stores document metadata and vector embeddings for semantic search |
| Cache | Redis | Caching for the backend, as listed in the project stack |
| AI | LLM APIs | Generates source-grounded answers from retrieved context |
| Containers | Docker | Local development and deployment packaging |
| Cloud | AWS | Deployment, as listed in the project stack |

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
  +--> PostgreSQL (pgvector): semantic search over document passages
  |
  +--> Redis: caching
  |
  +--> LLM APIs: RAG generation
  |
  v
Source-grounded answer (with sources)
```

### Upload flow

1. The user uploads a document through the React frontend.
2. The FastAPI backend receives the upload.
3. The document is prepared for retrieval (chunking and embedding are starter work, not implemented in this skeleton).

### Query / RAG flow

1. The user submits a question through the frontend.
2. The backend uses PostgreSQL (pgvector) semantic search to retrieve relevant passages from uploaded documents.
3. The retrieved passages are provided as context to LLM APIs.
4. The LLM APIs generate an answer grounded in those sources.
5. The backend returns the answer with its sources to the frontend.

## Why pgvector + Redis

- **PostgreSQL (pgvector):** The project uses PostgreSQL for document data, with pgvector for semantic search over embeddings, so retrieval and document storage stay in one database.
- **Redis:** Redis is listed in the project stack for caching. In this starter skeleton, its exact caching use is not implemented and is left as a TODO in the backend.

## AWS Deployment Sketch

This is a sketch, not a production deployment guide:

- **S3** — for storing uploaded documents.
- **EC2 / ECS** — for running the containerised backend and frontend (Docker).
- **RDS PostgreSQL** — for PostgreSQL with pgvector.
- **ElastiCache Redis** — for Redis.

No deployment, availability, or performance claims are made here.
