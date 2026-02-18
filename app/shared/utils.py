from typing import TypeVar, Sequence
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

T = TypeVar("T")

async def paginate(
    db: AsyncSession,
    base_query: Select,
    page: int,
    page_size: int,
) -> tuple[Sequence[T], int, int]:
    
    count_query = select(func.count()).select_from(base_query.order_by(None).subquery())
    total_count = await db.scalar(count_query)
    total_count = total_count or 0

    total_pages = (total_count + page_size - 1) // page_size

    paginated_query = (base_query.offset((page - 1) * page_size).limit(page_size))

    result = await db.execute(paginated_query)
    items = result.scalars().all()

    return items, total_count, total_pages
