from typing import Optional
from uuid import UUID

from sqlmodel import Field, Relationship

from app.models.base import BaseModel


class Flight(BaseModel, table=True):
    __tablename__ = "flights"

    trip_id: UUID = Field(foreign_key="trips.id")
    carrier: str
    flight_number: str
    origin: str
    destination: str
    depart_time: str
    arrive_time: str
    price: Optional[float] = None

    trip: "Trip" = Relationship(back_populates="flights")
