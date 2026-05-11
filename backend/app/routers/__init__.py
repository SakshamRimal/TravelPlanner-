from app.routers.auth import router as auth_router
from app.routers.trips import router as trips_router
from app.routers.ai import router as ai_router
from app.routers.recommendations import router as recommendations_router
from app.routers.budget import router as budget_router
from app.routers.destinations import router as destinations_router
from app.routers.chat import router as chat_router
from app.routers.users import router as users_router
from app.routers.weather import router as weather_router

__all__ = [
    "auth_router",
    "trips_router",
    "ai_router",
    "recommendations_router",
    "budget_router",
    "destinations_router",
    "chat_router",
    "users_router",
    "weather_router",
]
