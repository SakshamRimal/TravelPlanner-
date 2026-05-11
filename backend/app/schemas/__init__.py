from app.schemas.auth import LoginRequest, RefreshRequest, RegisterRequest, TokenResponse
from app.schemas.user import UserRead
from app.schemas.trip import TripCreate, TripRead, TripUpdate
from app.schemas.itinerary import ItineraryRead
from app.schemas.flight import FlightRead
from app.schemas.hotel import HotelRead
from app.schemas.activity import ActivityRead
from app.schemas.budget import BudgetRead
from app.schemas.chat import ChatRequest, ChatResponse, ChatHistoryRead
from app.schemas.destination import DestinationSearchRequest, DestinationRead
from app.schemas.ai import ItineraryGenerationRequest, ItineraryGenerationResponse
from app.schemas.recommendation import RecommendationResponse
from app.schemas.weather import WeatherResponse
from app.schemas.common import PaginatedResponse

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
    "FlightRead",
    "HotelRead",
    "ActivityRead",
    "BudgetRead",
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
