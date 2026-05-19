from uuid import UUID

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship

from app.models.base_model import BaseModel


class ChatHistory(BaseModel, table=True):
    __tablename__ = "chat_history"

    user_id: UUID = Field(foreign_key="users.id")
    role: str
    content: str
    metadata_json: dict | None = Field(sa_column=Column(JSONB))

    user: "User" = Relationship(back_populates="chats")
