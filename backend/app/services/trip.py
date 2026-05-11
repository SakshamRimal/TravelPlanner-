from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.trip import Trip
from app.repositories.trip import TripRepository
from app.utils.errors import NotFoundError


class TripService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = TripRepository(session)

    async def create_trip(self, user_id: str, data: dict) -> Trip:
        trip = Trip(user_id=user_id, **data)
        return await self.repo.add(trip)

    async def get_trip(self, trip_id: str) -> Trip:
        trip = await self.repo.get_by_id(trip_id)
        if not trip:
            raise NotFoundError("Trip not found")
        return trip

    async def list_trips(self, user_id: str):
        return await self.repo.list_by_user(user_id)

    async def update_trip(self, trip_id: str, data: dict) -> Trip:
        trip = await self.get_trip(trip_id)
        return await self.repo.update(trip, data)
