from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class FlightRead(BaseModel):
    id: UUID
    trip_id: UUID
    carrier: str
    flight_number: str
    origin: str
    destination: str
    depart_time: str
    arrive_time: str
    price: float | None
    created_at: datetime
