# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TravelPlanner is an AI-powered travel planning application with autonomous itinerary generation, recommendations, and chat assistance. It uses a FastAPI backend with PostgreSQL.

## Development Commands

### Docker (Recommended)

```bash
docker compose up --build
```

### Backend (Local)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic -c alembic/alembic.ini upgrade head
uvicorn app.main:app --reload
```

### Database Migrations

```bash
cd backend
alembic -c alembic/alembic.ini revision --autogenerate -m "migration_name"
alembic -c alembic/alembic.ini upgrade head
```

### Tests

```bash
cd backend
pytest app/tests -v
```

## Architecture

### Backend (FastAPI)

- **Routers** (`app/routers/`): 10 API endpoint modules (ai, auth, budget, chat, destinations, recommendations, trips, users, weather)
- **Services** (`app/services/`): Business logic layer with AI integration (Gemini), currency conversion, weather data
- **Repositories** (`app/repositories/`): Data access layer using SQLModel/SQLAlchemy async
- **Schemas** (`app/schemas/`): Pydantic request/response models
- **Core** (`app/core/`): Configuration, security (JWT), logging
- **Database**: PostgreSQL with asyncpg, managed via Alembic

### External Services

- Gemini (AI itinerary generation)
- SerpApi (search)
- Open-Meteo (weather - no API key required)
- AviationStack (flights)
- ExchangeRate API (currency conversion)

### Key Patterns

- JWT authentication with refresh token rotation
- User ownership checks on trip operations
- Rate limiting middleware (100 req/min)
- Request ID tracking for debugging
- Async database operations throughout

## Environment Variables

Required in `.env`:

- `DATABASE_URL` or `POSTGRES_*` values
- `JWT_SECRET` (generate a strong secret)
- `GEMINI_API_KEY` for AI features

Optional: `SERPAPI_API_KEY`, `AVIATIONSTACK_API_KEY`, `EXCHANGERATE_API_KEY`
