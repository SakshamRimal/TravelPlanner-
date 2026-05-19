from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat_model import ChatHistory
from app.repositories.base_repo import BaseRepository


class ChatRepository(BaseRepository[ChatHistory]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def list_by_user(self, user_id: str):
        result = await self.session.execute(
            select(ChatHistory).where(ChatHistory.user_id == user_id)
        )
        return result.scalars().all()
