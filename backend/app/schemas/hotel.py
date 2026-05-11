from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class HotelRead(BaseModel):
    id: UUID
    trip_id: UUID
    name: str
    address: str
    nightly_price: float | None
    rating: float | None
    created_at: datetime
