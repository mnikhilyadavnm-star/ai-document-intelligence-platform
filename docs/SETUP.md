# Setup

> Working portfolio implementation rebuilt from the resume description; not the original production code. No API key is required to run locally.

## Prerequisites

- Docker and Docker Compose (recommended path)
- Python 3.11+ (for running the backend without Docker)
- Node.js 18+ and npm (for running the frontend without Docker)

## Option 1: Docker Compose (recommended)

```bash
cp .env.example .env
docker compose up --build
```

Services and ports:

| Service | Port |
| --- | --- |
| Backend (FastAPI) | 8000 |
| Frontend (React) | 3000 |
| PostgreSQL (pgvector) | 5432 |
| Redis | 6379 |

Open:

- Frontend: `http://localhost:3000`
- Backend health check: `http://localhost:8000/health`
- API docs: `http://localhost:8000/docs`

Stop with `Ctrl+C`, then `docker compose down` (add `-v` to wipe the Postgres data volume).

## Option 2: Backend Only

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# Start Postgres (pgvector) and Redis, e.g. via docker compose:
docker compose -f ../docker-compose.yml up -d db redis
cp ../.env.example ../.env
uvicorn app.main:app --reload --port 8000
```

Check the health endpoint:

```bash
curl http://localhost:8000/health
```

Run the tests (no database, Redis, or API key needed):

```bash
python -m pytest tests/ -v
```

## Option 3: Frontend Only

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000`. The Vite dev server proxies `/documents`, `/query`, and `/health` to the backend on port 8000; set `VITE_API_URL` to point elsewhere if needed.

## Environment Variables

Copy `.env.example` to `.env`. Do not commit real keys or secrets. `LLM_API_KEY` is optional — leave it empty to use the free local TF-IDF + extractive RAG only.
