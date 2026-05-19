from pydantic import ConfigDict

from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.session import get_session
from app.schemas.trip_schema import TripCreate, TripRead, TripUpdate
from app.services.auth_service import get_current_user
from app.services.trip_service import TripService

router = APIRouter(prefix="/trips", tags=["Trips"])


@router.post("", response_model=TripRead, status_code=status.HTTP_201_CREATED)
async def create_trip(
    payload: TripCreate,
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user),
):
    service = TripService(session)
    trip = await service.create_trip(str(user.id), payload.model_dump())
    return TripRead.model_validate(trip)


@router.get("", response_model=list[TripRead])
async def list_trips(
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user),
):
    service = TripService(session)
    trips = await service.list_trips(str(user.id))
    return [TripRead.model_validate(trip) for trip in trips]


@router.get("/{trip_id}", response_model=TripRead)
async def get_trip(
    trip_id: str,
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user),
):
    service = TripService(session)
    trip = await service.get_trip(trip_id, str(user.id))
    return TripRead.model_validate(trip)


@router.patch("/{trip_id}", response_model=TripRead)
async def update_trip(
    trip_id: str,
    payload: TripUpdate,
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user),
):
    service = TripService(session)
    trip = await service.update_trip(trip_id, payload.model_dump(exclude_none=True), str(user.id))
    return TripRead.model_validate(trip)


@router.delete("/{trip_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_trip(
    trip_id: str,
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user),
):
    service = TripService(session)
    await service.delete_trip(trip_id, str(user.id))
