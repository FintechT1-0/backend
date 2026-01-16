from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.api.courses.schemas import (
    CourseCreate, CourseUpdate, CourseView,
    PaginationInfo, CourseId, CourseFilter
)
from app.models import Course
from datetime import datetime
from app.api.auth.schemas import CurrentUser
from app.api.courses.errors import InsufficientRights, InsufficientFilterRights
from app.api.courses.utils import build_course_filters
from typing import Optional, List


async def create_course(db: AsyncSession, course: CourseCreate) -> CourseId:
    db_course = Course(**course.model_dump(mode="json"))
    db.add(db_course)
    await db.commit()
    await db.refresh(db_course)
    return CourseId(id=db_course.id)


async def delete_course(db: AsyncSession, course: Course):
    await db.delete(course)
    await db.commit()


async def patch_course(course_update: CourseUpdate, course: Course, db: AsyncSession) -> CourseView:
    for field_name, field_value in course_update.model_dump(exclude_unset=True, mode="json").items():
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
    tags: Optional[List[str]],
    parameters: CourseFilter,
    db: AsyncSession, 
    current_user: CurrentUser,
) -> PaginationInfo:
    if current_user.role != "admin" and parameters.isPublished != None:
        raise InsufficientFilterRights

    filters = build_course_filters(tags, parameters)

    query = select(Course).filter(*filters)

    total_courses_result = await db.execute(query)
    total_courses = len(total_courses_result.scalars().all())
    total_pages = (total_courses + parameters.page_size - 1) // parameters.page_size

    query = query.offset((parameters.page - 1) * parameters.page_size).limit(parameters.page_size)
    result = await db.execute(query)
    courses = result.scalars().all()

    return PaginationInfo(
        courses=[CourseView.from_orm(course) for course in courses],
        current_page=parameters.page,
        page_size=len(courses),
        total_courses=total_courses,
        total_pages=total_pages
    )
