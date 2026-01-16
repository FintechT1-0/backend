from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_
from fastapi import Depends
from app.models import Course
from app.database import get_async_db
from fastapi import HTTPException
from typing import Optional, List
from sqlalchemy.future import select
from loguru import logger
from app.api.courses.schemas import CourseFilter


async def get_course_by_id(id: int, db: AsyncSession = Depends(get_async_db)) -> Course:
    result = await db.execute(select(Course).filter(Course.id == id))
    item = result.scalars().first()
    if item is None:
        raise HTTPException(status_code=404, detail="No course with this id.")
    return item


def build_course_filters(tags: Optional[List[str]], parameters: CourseFilter):
    
    def add_filter(condition):
        if condition is not None:
            filters.append(condition)

    filters = []

    if tags and len(tags) > 0:
        tags = [item.lower() for item in tags]
        logger.debug(f"Received tags: {tags}")

    
    add_filter(
        or_(
            Course.description_en.ilike(f"%{parameters.description}%"),
            Course.description_ua.ilike(f"%{parameters.description}%")
        ) if parameters.description else None
    )

    add_filter(
        or_(
            Course.title_en.ilike(f"%{parameters.title}%"),
            Course.title_ua.ilike(f"%{parameters.title}%")
        ) if parameters.title else None
    )

    add_filter(Course.category.ilike(f"%{parameters.category}%") if parameters.category else None)
    add_filter(Course.tags.overlap(tags) if tags else None)

    add_filter(Course.durationText.ilike(f"%{parameters.durationText}%") if parameters.durationText else None)


    add_filter(Course.price >= parameters.price_min if parameters.price_min else None)
    add_filter(Course.price <= parameters.price_max if parameters.price_max else None)

    add_filter(Course.link.ilike(f"%{parameters.link}%") if parameters.link else None)
    add_filter(Course.speaker.ilike(f"%{parameters.speaker}%") if parameters.speaker else None)
    add_filter(Course.image.ilike(f"%{parameters.image}%") if parameters.image else None)

    add_filter(Course.isPublished == parameters.isPublished if parameters.isPublished else None)
    
    return filters
