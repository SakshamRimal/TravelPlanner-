from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.session import get_session
from app.schemas.trip import TripCreate, TripRead, TripUpdate
from app.services.auth import get_current_user
from app.services.trip import TripService

router = APIRouter(prefix="/trips", tags=["Trips"])


@router.post("", response_model=TripRead)
async def create_trip(
    payload: TripCreate,
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user),
):
    service = TripService(session)
    trip = await service.create_trip(str(user.id), payload.model_dump())
    return TripRead(**trip.dict())


@router.get("", response_model=list[TripRead])
async def list_trips(
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user),
):
    service = TripService(session)
    trips = await service.list_trips(str(user.id))
    return [TripRead(**trip.dict()) for trip in trips]


@router.get("/{trip_id}", response_model=TripRead)
async def get_trip(
    trip_id: str,
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user),
):
    service = TripService(session)
    trip = await service.get_trip(trip_id)
    return TripRead(**trip.dict())


@router.patch("/{trip_id}", response_model=TripRead)
async def update_trip(
    trip_id: str,
    payload: TripUpdate,
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user),
):
    service = TripService(session)
    trip = await service.update_trip(trip_id, payload.model_dump(exclude_none=True))
    return TripRead(**trip.dict())
