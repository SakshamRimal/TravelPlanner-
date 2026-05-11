from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ItineraryRead(BaseModel):
    id: UUID
    trip_id: UUID
    day: int
    summary: str
    items: dict | None
    created_at: datetime
