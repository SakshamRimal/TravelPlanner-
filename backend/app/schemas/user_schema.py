from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr


class UserRead(BaseModel):
    id: UUID
    email: EmailStr
    full_name: str | None
    is_active: bool
    created_at: datetime
