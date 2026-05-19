from app.routers.auth_router import router as auth_router
from app.routers.trips_router import router as trips_router
from app.routers.ai_router import router as ai_router
from app.routers.recommendations_router import router as recommendations_router
from app.routers.budget_router import router as budget_router
from app.routers.destinations_router import router as destinations_router
from app.routers.chat_router import router as chat_router
from app.routers.users_router import router as users_router
from app.routers.weather_router import router as weather_router
from app.routers.maps_router import router as maps_router

__all__ = [
    "auth_router",
    "trips_router",
    "ai_router",
    "recommendations_router",
    "budget_router",
    "destinations_router",
    "chat_router",
    "maps_router",
    "users_router",
    "weather_router",
]
