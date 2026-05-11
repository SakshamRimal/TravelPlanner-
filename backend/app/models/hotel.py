from typing import Optional
from uuid import UUID

from sqlmodel import Field, Relationship

from app.models.base import BaseModel


class Hotel(BaseModel, table=True):
    __tablename__ = "hotels"

    trip_id: UUID = Field(foreign_key="trips.id")
    name: str
    address: str
    nightly_price: Optional[float] = None
    rating: Optional[float] = None

    trip: "Trip" = Relationship(back_populates="hotels")
