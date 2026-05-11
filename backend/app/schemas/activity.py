from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ActivityRead(BaseModel):
    id: UUID
    trip_id: UUID
    name: str
    category: str
    location: str
    cost: float | None
    created_at: datetime
