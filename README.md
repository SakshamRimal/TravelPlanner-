# TravelPlanner

AI-powered travel planner with autonomous itinerary generation, recommendations, and chat assistance.

## Architecture

- Backend: FastAPI + SQLModel + Alembic + PostgreSQL
- AI/External Services: Gemini, SerpApi, Open-Meteo, ExchangeRate API

## Prerequisites

- Python 3.11+
- Node.js 20+
- PostgreSQL 16+

## Environment Setup

1. Copy env template:

```bash
cp .env.example .env
```

2. Update required values in `.env`:

- `DATABASE_URL` (or `POSTGRES_*` values)
- `JWT_SECRET`
- Optional provider keys (`GEMINI_API_KEY`, `SERPAPI_API_KEY`, etc.)

## Run With Docker

```bash
docker compose up --build
```

Services:

- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Run Locally (Without Docker)

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic -c alembic/alembic.ini upgrade head
uvicorn app.main:app --reload
```

## Database Migrations

```bash
cd backend
alembic -c alembic/alembic.ini upgrade head
```

Create a new migration:

```bash
alembic -c alembic/alembic.ini revision --autogenerate -m "your_migration_name"
```

## Testing

Backend tests:

```bash
cd backend
pytest app/tests -v
```

## Main Features

- JWT auth with refresh token rotation
- Trip CRUD with user ownership checks
- AI itinerary generation
- Recommendations (flights, hotels, activities)
- Budget estimation
- Weather forecast lookup
- Chat assistant with optional trip context
