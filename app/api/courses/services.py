from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.api.courses.schemas import (
    CourseCreate, CourseUpdate, CourseView,
    PaginationInfo
)
from app.models import Course
from datetime import datetime
from app.api.auth.schemas import CurrentUser
from app.api.courses.errors import InsufficientRights, InsufficientFilterRights
from app.api.courses.utils import build_course_filters
from typing import Optional


async def create_course(db: AsyncSession, course: CourseCreate):
    db_course = Course(**course.dict())
    db.add(db_course)
    await db.commit()


async def delete_course(db: AsyncSession, course: Course):
    await db.delete(course)
    await db.commit()


async def patch_course(course_update: CourseUpdate, course: Course, db: AsyncSession) -> CourseView:
    for field_name, field_value in course_update.dict(exclude_unset=True).items():
        setattr(course, field_name, field_value)

    course.updatedAt = datetime.utcnow()

    await db.commit()
    await db.refresh(course)

    return CourseView.from_orm(course)


def try_get_course(course: Course, current_user: CurrentUser) -> CourseView:
    if current_user.role != "admin" and course.isPublished == False:
        raise InsufficientRights
    
    return CourseView.from_orm(course)


async def filter_courses(
    db: AsyncSession, 
    current_user: CurrentUser,
    tags: Optional[str] = None,
    lang: Optional[str] = None,
    title: Optional[str] = None,
    description: Optional[str] = None,
    link: Optional[str] = None,
    durationText: Optional[str] = None,
    price_min: Optional[float] = None,
    price_max: Optional[float] = None,
    isPublished: Optional[bool] = None,
    page: int = 1,
    page_size: int = 20
) -> PaginationInfo:
    if current_user.role != "admin" and isPublished != None:
        raise InsufficientFilterRights

    filters = build_course_filters(lang, tags, title, description, link, durationText, price_min, price_max, isPublished)

    query = select(Course).filter(*filters)

    total_courses_result = await db.execute(query)
    total_courses = len(total_courses_result.scalars().all())
    total_pages = (total_courses + page_size - 1) // page_size

    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    courses = result.scalars().all()

    return PaginationInfo(
        courses=[CourseView.from_orm(course) for course in courses],
        current_page=page,
        page_size=len(courses),
        total_courses=total_courses,
        total_pages=total_pages
    )
