from typing import Optional
from uuid import UUID

from sqlmodel import Field, Relationship

from app.models.base import BaseModel


class Activity(BaseModel, table=True):
    __tablename__ = "activities"

    trip_id: UUID = Field(foreign_key="trips.id")
    name: str
    category: str
    location: str
    cost: Optional[float] = None

    trip: "Trip" = Relationship(back_populates="activities")
