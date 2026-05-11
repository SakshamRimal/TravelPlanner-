from typing import Optional
from uuid import UUID

from sqlmodel import Field, Relationship

from app.models.base import BaseModel


class Budget(BaseModel, table=True):
    __tablename__ = "budgets"

    trip_id: UUID = Field(foreign_key="trips.id", unique=True)
    currency: str = Field(default="USD")
    total_estimate: Optional[float] = None
    breakdown: Optional[str] = None

    trip: "Trip" = Relationship(back_populates="budget_detail")
