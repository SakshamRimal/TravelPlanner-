from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.trip_model import Trip
from app.repositories.trip_repo import TripRepository
from app.utils.errors import NotFoundError


class TripService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = TripRepository(session)

    async def create_trip(self, user_id: str, data: dict) -> Trip:
        trip = Trip(user_id=user_id, **data)
        return await self.repo.add(trip)

    async def get_trip(self, trip_id: str, user_id: str | None = None) -> Trip:
        trip = await self.repo.get_by_id(trip_id)
        if not trip:
            raise NotFoundError("Trip not found")
        if user_id and str(trip.user_id) != user_id:
            raise NotFoundError("Trip not found")
        return trip

    async def list_trips(self, user_id: str):
        return await self.repo.list_by_user(user_id)

    async def update_trip(self, trip_id: str, data: dict, user_id: str) -> Trip:
        trip = await self.get_trip(trip_id, user_id)
        return await self.repo.update(trip, data)

    async def delete_trip(self, trip_id: str, user_id: str) -> None:
        trip = await self.get_trip(trip_id, user_id)
        await self.repo.delete(trip)
