from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.chat_schema import ChatRequest, ChatResponse
from app.services.auth_service import get_current_user
from app.services.chat_service import ChatService
from app.services.trip_service import TripService
from app.models.user_model import User

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    service = ChatService()
    context_str = None
    if payload.trip_id:
        trip_service = TripService(session)
        try:
            trip = await trip_service.get_trip(payload.trip_id, str(current_user.id))
            context_str = (
                f"Trip to {trip.destination}: {trip.start_date} to {trip.end_date}, "
                f"Budget: Rs.{trip.budget or 'N/A'}, "
                f"Travelers: {trip.travelers}, "
                f"Interests: {trip.interests or 'N/A'}, "
                f"Transport: {trip.transport or 'N/A'}, "
                f"Accommodation: {trip.accommodation or 'N/A'}, "
                f"Notes: {payload.message}"
            )
        except Exception:
            context_str = None
    return await service.reply(payload.message, context_str)
