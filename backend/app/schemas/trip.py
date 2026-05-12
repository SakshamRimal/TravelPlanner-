from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel


class TripCreate(BaseModel):
    origin: str
    destination: str
    budget: float | None = None
    travelers: int = 1
    start_date: date
    end_date: date
    interests: str | None = None
    transport: str | None = None
    accommodation: str | None = None


class TripUpdate(BaseModel):
    origin: str | None = None
    destination: str | None = None
    budget: float | None = None
    travelers: int | None = None
    start_date: date | None = None
    end_date: date | None = None
    interests: str | None = None
    transport: str | None = None
    accommodation: str | None = None
    status: str | None = None


class TripRead(BaseModel):
    id: UUID
    origin: str
    destination: str
    budget: float | None
    travelers: int
    start_date: date
    end_date: date
    interests: str | None
    transport: str | None
    accommodation: str | None
    status: str
    created_at: datetime
