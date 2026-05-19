from typing import Optional
from uuid import UUID

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship

from app.models.base_model import BaseModel


class Itinerary(BaseModel, table=True):
    __tablename__ = "itineraries"

    trip_id: UUID = Field(foreign_key="trips.id")
    day: int
    summary: str
    items: Optional[dict] = Field(sa_column=Column(JSONB))

    trip: "Trip" = Relationship(back_populates="itineraries")
