from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class BudgetRead(BaseModel):
    id: UUID
    trip_id: UUID
    currency: str
    total_estimate: float | None
    breakdown: str | None
    created_at: datetime
