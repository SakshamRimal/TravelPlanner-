from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class DestinationSearchRequest(BaseModel):
    query: str


class DestinationRead(BaseModel):
    id: UUID
    user_id: UUID
    name: str
    country: str
    notes: str | None
    created_at: datetime
