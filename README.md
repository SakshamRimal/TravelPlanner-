# TravelPlanner

AI-powered travel planner with autonomous itinerary generation, recommendations, and chat assistance.

## Tech stack

- Frontend: Next.js, TypeScript, Tailwind CSS, ShadCN UI, React Query, Axios
- Backend: FastAPI, SQLModel, PostgreSQL, Alembic
- AI: LangChain with Gemini provider
- Infra: Docker, Docker Compose

## Quick start (local)

1. Copy env file:
   - `cp .env.example .env`
2. Run with Docker:
   - `docker compose up --build`
3. Backend API:
   - http://localhost:8000/docs
4. Frontend:
   - http://localhost:3000

## Project structure

- `frontend/` Next.js app
- `backend/` FastAPI app

## Example prompts

- "Plan a 5-day budget trip to Pokhara under $500 including hiking and local food."
- "Create a 3-day itinerary for Kyoto focused on temples and food markets, mid-range budget."

## Example API requests

- Auth register: `POST /api/v1/auth/register`
- Auth login: `POST /api/v1/auth/login`
- Create trip: `POST /api/v1/trips`
- Generate itinerary: `POST /api/v1/ai/itinerary`
- Chat: `POST /api/v1/chat`

## Notes

- Hotels default to LiteAPI when configured, otherwise mocked.
- Flights are still mocked for now until the flight LiteAPI endpoint is added.
- Weather data is served from Open-Meteo (no API key required).
- Replace placeholder API keys in `.env` when enabling external providers.
