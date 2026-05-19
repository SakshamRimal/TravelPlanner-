from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    trip_id: str | None = None


class ChatResponse(BaseModel):
    reply: str
    created_at: datetime


class ChatHistoryRead(BaseModel):
    id: UUID
    user_id: UUID
    role: str
    content: str
    created_at: datetime
