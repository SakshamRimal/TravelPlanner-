from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.chat import ChatHistory
from app.repositories.base import BaseRepository


class ChatRepository(BaseRepository[ChatHistory]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def list_by_user(self, user_id: str):
        result = await self.session.exec(
            select(ChatHistory).where(ChatHistory.user_id == user_id)
        )
        return result.all()
