from app.schemas.auth_schema import LoginRequest, RefreshRequest, RegisterRequest, TokenResponse
from app.schemas.user_schema import UserRead
from app.schemas.trip_schema import TripCreate, TripRead, TripUpdate
from app.schemas.itinerary_schema import ItineraryRead
from app.schemas.chat_schema import ChatRequest, ChatResponse, ChatHistoryRead
from app.schemas.destination_schema import DestinationSearchRequest, DestinationRead
from app.schemas.ai_schema import ItineraryGenerationRequest, ItineraryGenerationResponse
from app.schemas.recommendation_schema import RecommendationResponse
from app.schemas.weather_schema import WeatherResponse
from app.schemas.common_schema import PaginatedResponse
__all__ = [
    "LoginRequest",
    "RefreshRequest",
    "RegisterRequest",
    "TokenResponse",
    "UserRead",
    "TripCreate",
    "TripRead",
    "TripUpdate",
    "ItineraryRead",
    "ChatRequest",
    "ChatResponse",
    "ChatHistoryRead",
    "DestinationSearchRequest",
    "DestinationRead",
    "ItineraryGenerationRequest",
    "ItineraryGenerationResponse",
    "RecommendationResponse",
    "WeatherResponse",
    "PaginatedResponse",
]