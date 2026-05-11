from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.trip import Trip
from app.repositories.base import BaseRepository


class TripRepository(BaseRepository[Trip]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_id(self, trip_id: str) -> Trip | None:
        result = await self.session.exec(select(Trip).where(Trip.id == trip_id))
        return result.first()

    async def list_by_user(self, user_id: str):
        result = await self.session.exec(select(Trip).where(Trip.user_id == user_id))
        return result.all()
