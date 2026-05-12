from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.auth import get_current_user
from app.services.chat import ChatService
from app.models.user import User

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    service = ChatService()
    context = None
    if payload.trip_id:
        pass
    return await service.reply(payload.message, context)
