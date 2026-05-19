from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.core.config import get_settings
from app.core.logging import setup_logging
from app.utils.rate_limit import RateLimitMiddleware
from app.routers import (
    ai_router,
    auth_router,
    budget_router,
    chat_router,
    destinations_router,
    recommendations_router,
    trips_router,
    users_router,
    weather_router,
)

setup_logging()
settings = get_settings()

app = FastAPI(title="TravelPlanner API", version="0.1.0")

app.add_middleware(RateLimitMiddleware, limit=100, window_seconds=60)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(trips_router, prefix="/api/v1")
app.include_router(ai_router, prefix="/api/v1")
app.include_router(recommendations_router, prefix="/api/v1")
app.include_router(budget_router, prefix="/api/v1")
app.include_router(destinations_router, prefix="/api/v1")
app.include_router(chat_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(weather_router, prefix="/api/v1")
from app.routers import maps_router
app.include_router(maps_router , prefix="/api/v1")



@app.get("/health")
async def health():
    return {"status": "ok"}
