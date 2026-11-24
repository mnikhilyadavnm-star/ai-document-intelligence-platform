# Setup

> Portfolio documentation and starter skeleton based on the resume description; not the original production code.

## Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for running the backend without Docker)
- Node.js 18+ and npm (for running the frontend without Docker)
- A PostgreSQL database with pgvector and a Redis instance, or Docker Compose to provide them locally

## Option 1: Docker Compose

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

Note: the backend and frontend services in `docker-compose.yml` are placeholders. The endpoints in the backend are starter stubs, so the full upload and query flow is not implemented in this skeleton.

## Option 2: Backend Only

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp ../.env.example ../.env
uvicorn app.main:app --reload --port 8000
```

Check the health endpoint:

```bash
curl http://localhost:8000/health
```

## Option 3: Frontend Only

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000`.

Note: the frontend is a minimal starter placeholder in `src/App.jsx`, with fetch stubs and no completed API wiring.

## Environment Variables

Copy `.env.example` to `.env` and fill in the placeholders. Do not commit real keys or secrets. See `.env.example` in the repository root.
