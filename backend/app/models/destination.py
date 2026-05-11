from uuid import UUID

from sqlmodel import Field, Relationship

from app.models.base import BaseModel


class SavedDestination(BaseModel, table=True):
    __tablename__ = "saved_destinations"

    user_id: UUID = Field(foreign_key="users.id")
    name: str
    country: str
    notes: str | None = None

    user: "User" = Relationship(back_populates="saved_destinations")
