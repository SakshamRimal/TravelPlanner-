from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.trip import Trip
from app.repositories.base import BaseRepository


class TripRepository(BaseRepository[Trip]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_id(self, trip_id: str) -> Trip | None:
        result = await self.session.execute(select(Trip).where(Trip.id == trip_id))
        return result.scalar_one_or_none()

    async def list_by_user(self, user_id: str):
        result = await self.session.execute(select(Trip).where(Trip.user_id == user_id))
        return result.scalars().all()
