from typing import Sequence, Tuple

from sqlalchemy import Select, func
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession


async def paginate(
    session: AsyncSession,
    statement: Select,
    page: int = 1,
    size: int = 20,
) -> Tuple[Sequence, int]:
    offset = (page - 1) * size
    count_stmt = select(func.count()).select_from(statement.subquery())
    total = (await session.exec(count_stmt)).one()
    results = await session.exec(statement.offset(offset).limit(size))
    return results.all(), total
