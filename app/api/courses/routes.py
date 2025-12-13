from fastapi import APIRouter, Depends, status, Response, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.courses.schemas import (
    CourseCreate, CourseUpdate, CourseView,
    PaginationInfo
)
from app.api.auth.services import (
    get_admin, get_user
)
from app.database import get_async_db
from app.api.courses.services import (
    create_course, delete_course, patch_course,
    try_get_course, filter_courses
)
from app.api.auth.schemas import CurrentUser
from app.models import Course
from app.api.courses.utils import get_course_by_id
from app.api.courses.errors import InsufficientRights, InsufficientFilterRights
from typing import Optional, List


course_router = APIRouter()


@course_router.post("/", tags=["Courses", "Admin"])
async def admin_create_course(
    course: CourseCreate, 
    db: AsyncSession = Depends(get_async_db), 
    current_user: CurrentUser = Depends(get_admin)
) -> Response:
    """ Creates a new course. """
    await create_course(db, course)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@course_router.delete("/{id}", tags=["Courses", "Admin"])
async def admin_delete_course(
    id: int, 
    course: Course = Depends(get_course_by_id), 
    current_user: CurrentUser = Depends(get_admin),
    db: AsyncSession = Depends(get_async_db)
) -> Response:
    """ Deletes a course by ID. """
    await delete_course(db, course)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@course_router.patch("/{id}", tags=["Courses", "Admin"])
async def admin_patch_course(
    id: int,
    update: CourseUpdate,
    course: Course = Depends(get_course_by_id),
    current_user: CurrentUser = Depends(get_admin),
    db: AsyncSession = Depends(get_async_db)
) -> CourseView:
    """ Patches (updates) a course by ID. """
    return await patch_course(update, course, db)


@course_router.get("/{id}", tags=["Courses"],
                   responses={
                       403: { "description": "Insufficient rights to retrieve the course" }
                   })
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


@course_router.get("/", tags=["Courses"],
                   responses={
                       403: { "description": "Insufficient rights to apply particular filters" }
                   })
async def get_multiple_courses(
    tags: Optional[List[str]] = Query(None),
    lang: Optional[str] = None,
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

    To send an array of query parameters, use following syntax:
    http://127.0.0.1:8000/courses/?tags=AI for Fintech&tags=Fintech, Digital Finance %26 Virtual Assets
    """
    try:
        return await filter_courses(
            db, current_user, tags,
            lang, title, description, 
            link, durationText, price_min, 
            price_max, isPublished, page, 
            page_size
        )
    except InsufficientFilterRights as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message)
