from typing import List, Optional
from uuid import UUID

from sqlmodel import Field, Relationship

from app.models.base_model import BaseModel


class User(BaseModel, table=True):
    __tablename__ = "users"

    email: str = Field(unique=True, index=True)
    full_name: Optional[str] = None
    hashed_password: str
    is_active: bool = Field(default=True)

    trips: List["Trip"] = Relationship(back_populates="user")
    chats: List["ChatHistory"] = Relationship(back_populates="user")
    saved_destinations: List["SavedDestination"] = Relationship(back_populates="user")
