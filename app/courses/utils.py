from sqlalchemy.orm import Session
from sqlalchemy import or_, cast, String
from fastapi import Depends
from app.models import Course
from app.database import get_db
from fastapi import HTTPException
from typing import Optional
from loguru import logger


def get_course_by_id(id: int, db: Session = Depends(get_db)) -> Course:
    item = db.query(Course).filter(Course.id == id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="No course with this id.")
    return item


def build_course_filters(
    tags: Optional[str],
    title: Optional[str],
    description: Optional[str],
    link: Optional[str],
    durationText: Optional[str],
    price_min: Optional[float],
    price_max: Optional[float],
    isPublished: Optional[bool]
):
    
    def add_filter(condition):
        if condition is not None:
            filters.append(condition)

    filters = []
    
    if tags is not None:
        tags = tags.split(',')

    add_filter(Course.tags.overlap(tags) if tags else None)
    add_filter(
        or_(
            Course.title.op('->>')('ua').ilike(f"%{title}%") if title else None,
            Course.title.op('->>')('en').ilike(f"%{title}%") if title else None
        ) if title else None
    )
    add_filter(
        or_(
            Course.description.op('->>')('ua').ilike(f"%{description}%") if description else None,
            Course.description.op('->>')('en').ilike(f"%{description}%") if description else None
        ) if description else None
    )
    add_filter(Course.link.ilike(f"%{link}%") if link else None)
    add_filter(Course.durationText.ilike(f"%{durationText}%") if durationText else None)
    add_filter(Course.price >= price_min if price_min is not None else None)
    add_filter(Course.price <= price_max if price_max is not None else None)
    add_filter(Course.isPublished == isPublished if isPublished is not None else None)
    
    return filters