from datetime import date
from typing import List, Optional
from uuid import UUID

from sqlmodel import Field, Relationship

from app.models.base import BaseModel


class Trip(BaseModel, table=True):
    __tablename__ = "trips"

    user_id: UUID = Field(foreign_key="users.id")
    destination: str
    budget: Optional[float] = None
    travelers: int = 1
    start_date: date
    end_date: date
    interests: Optional[str] = None
    transport: Optional[str] = None
    accommodation: Optional[str] = None
    status: str = Field(default="planned")

    user: "User" = Relationship(back_populates="trips")
    itineraries: List["Itinerary"] = Relationship(back_populates="trip")
    flights: List["Flight"] = Relationship(back_populates="trip")
    hotels: List["Hotel"] = Relationship(back_populates="trip")
    activities: List["Activity"] = Relationship(back_populates="trip")
    budget_detail: Optional["Budget"] = Relationship(back_populates="trip")
