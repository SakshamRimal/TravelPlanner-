from datetime import datetime
from typing import Any, Generic, TypeVar

from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncSession

ModelType = TypeVar("ModelType", bound=SQLModel)


class BaseRepository(Generic[ModelType]):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, instance: ModelType) -> ModelType:
        self.session.add(instance)
        await self.session.commit()
        await self.session.refresh(instance)
        return instance

    async def update(self, instance: ModelType, data: dict[str, Any], allowed_fields: set[str] | None = None) -> ModelType:
        for key, value in data.items():
            if allowed_fields is not None and key not in allowed_fields:
                continue
            if value is not None:
                setattr(instance, key, value)
        if hasattr(instance, "updated_at"):
            setattr(instance, "updated_at", datetime.utcnow())
        await self.session.commit()
        await self.session.refresh(instance)
        return instance

    async def delete(self, instance: ModelType) -> None:
        await self.session.delete(instance)
        await self.session.commit()
