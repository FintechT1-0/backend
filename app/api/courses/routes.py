from fastapi import APIRouter, Depends, status, Response, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.courses.schemas import (
    CourseCreate, CourseUpdate, CourseView,
    PaginationInfo, CourseId, CourseFilter
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
from app.docs import admin_required, user_required, privilege_required

from loguru import logger


course_router = APIRouter()


@course_router.post("/", tags=["Courses", "Admin"],
                    responses={
                        **admin_required,
                        **privilege_required
                    })
async def admin_create_course(
    course: CourseCreate, 
    db: AsyncSession = Depends(get_async_db), 
    current_user: CurrentUser = Depends(get_admin)
) -> CourseId:
    """ Creates a new course. """
    return await create_course(db, course)


@course_router.delete("/{id}", tags=["Courses", "Admin"],
                      responses={
                          **admin_required,
                          **privilege_required
                      })
async def admin_delete_course(
    id: int, 
    course: Course = Depends(get_course_by_id), 
    current_user: CurrentUser = Depends(get_admin),
    db: AsyncSession = Depends(get_async_db)
) -> Response:
    """ Deletes a course by ID. """
    await delete_course(db, course)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@course_router.patch("/{id}", tags=["Courses", "Admin"],
                     responses={
                         **admin_required,
                         **privilege_required
                     })
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
                       **user_required,
                       403: { "description": InsufficientRights.message }
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
                       **user_required,
                       403: { "description": InsufficientFilterRights.message }
                   })
async def get_multiple_courses(
    tags: Optional[List[str]] = Query(None),
    parameters: CourseFilter = Depends(),
    db: AsyncSession = Depends(get_async_db), 
    current_user: CurrentUser = Depends(get_user)
) -> PaginationInfo:
    """
    Retrieves multiple courses with filters and pagination.
    `tags` should be a comma-separated string.

    To send an array of query parameters, use following syntax:
    http://127.0.0.1:8000/courses/?tags=AI for Fintech&tags=Fintech, Digital Finance %26 Virtual Assets
    """

    logger.debug(parameters)
    try:
        return await filter_courses(tags, parameters, db, current_user)
    except InsufficientFilterRights as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message)
