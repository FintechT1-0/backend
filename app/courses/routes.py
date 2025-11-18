from fastapi import APIRouter, Depends, status, Response, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.courses.schemas import (
    CourseCreate, CourseUpdate, CourseView,
    PaginationInfo
)
from app.auth.services import (
    get_admin, get_user
)
from app.database import get_async_db
from app.courses.services import (
    create_course, delete_course, patch_course,
    try_get_course, filter_courses
)
from app.auth.schemas import CurrentUser
from app.models import Course
from app.courses.utils import get_course_by_id
from app.courses.errors import InsufficientRights, InsufficientFilterRights
from typing import Optional


course_router = APIRouter()


@course_router.post("/")
async def admin_create_course(
    course: CourseCreate, 
    db: AsyncSession = Depends(get_async_db), 
    current_user: CurrentUser = Depends(get_admin)
) -> Response:
    """ Creates a new course. """
    await create_course(db, course)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@course_router.delete("/{id}")
async def admin_delete_course(
    id: int, 
    course: Course = Depends(get_course_by_id), 
    current_user: CurrentUser = Depends(get_admin),
    db: AsyncSession = Depends(get_async_db)
) -> Response:
    """ Deletes a course by ID. """
    await delete_course(db, course)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@course_router.patch("/{id}")
async def admin_patch_course(
    id: int,
    update: CourseUpdate,
    course: Course = Depends(get_course_by_id),
    current_user: CurrentUser = Depends(get_admin),
    db: AsyncSession = Depends(get_async_db)
) -> CourseView:
    """ Patches (updates) a course by ID. """
    return await patch_course(update, course, db)


@course_router.get("/{id}")
async def get_single_course(
    id: int,
    course: Course = Depends(get_course_by_id),
    current_user: CurrentUser = Depends(get_user)
) -> CourseView:
    """
    Retrieves a single course by ID.
    Raises HTTP 403 if insufficient rights.
    """
    try:
        return try_get_course(course, current_user)
    except InsufficientRights as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message)


@course_router.get("/")
async def get_multiple_courses(
    tags: Optional[str] = None,
    title: Optional[str] = None,
    description: Optional[str] = None,
    link: Optional[str] = None,
    durationText: Optional[str] = None,
    price_min: Optional[float] = Query(None, ge=0),
    price_max: Optional[float] = Query(None, ge=0),
    isPublished: Optional[bool] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_async_db), 
    current_user: CurrentUser = Depends(get_user)
) -> PaginationInfo:
    """
    Retrieves multiple courses with filters and pagination.
    `tags` should be a comma-separated string.
    """
    try:
        return await filter_courses(
            db, current_user, tags, 
            title, description, link, 
            durationText, price_min, price_max, 
            isPublished, page, page_size
        )
    except InsufficientFilterRights as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message)
