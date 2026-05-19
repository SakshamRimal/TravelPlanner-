from datetime import datetime
from uuid import UUID

from sqlmodel import Field

from app.models.base_model import BaseModel


class RefreshToken(BaseModel, table=True):
    __tablename__ = "refresh_tokens"

    user_id: UUID = Field(foreign_key="users.id")
    token_hash: str
    expires_at: datetime
    revoked: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)