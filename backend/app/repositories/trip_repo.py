from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.trip_model import Trip
from app.repositories.base_repo import BaseRepository


class TripRepository(BaseRepository[Trip]):
    UPDATABLE_FIELDS = {"title", "origin", "destination", "budget", "travelers", "start_date", "end_date", "interests", "transport", "accommodation", "status"}

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_id(self, trip_id: str) -> Trip | None:
        result = await self.session.execute(select(Trip).where(Trip.id == trip_id))
        return result.scalar_one_or_none()

    async def list_by_user(self, user_id: str):
        result = await self.session.execute(select(Trip).where(Trip.user_id == user_id))
        return result.scalars().all()

    async def update(self, instance: Trip, data: dict) -> Trip:
        return await super().update(instance, data, allowed_fields=self.UPDATABLE_FIELDS)
