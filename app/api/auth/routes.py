from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.auth.schemas import (
    CurrentUser, UserLogin, UserCreate, 
    UserInfo, LoginResponse, EmailCheck, 
    CheckResult
)
from app.api.auth.services import (
    get_user, try_login, create_user, 
    check_email
)
from app.database import get_async_db
from app.api.auth.errors import (
    InvalidCredentials, CredentialsAlreadyTaken, InvalidAdminPassword
)


auth_router = APIRouter()


@auth_router.post("/checkEmail", tags=["Registration"])
async def check_existing_email(data: EmailCheck, db: AsyncSession = Depends(get_async_db)) -> CheckResult:
    """Check if an email is already registered."""

    return await check_email(data, db)


@auth_router.get("/me", tags=["Info"])
async def get_me(current_user: CurrentUser = Depends(get_user)) -> UserInfo:
    """Retrieve the currently authenticated user by token."""

    return current_user


@auth_router.post("/register", tags=["Registration"],
                  responses={
                      400: { "description": "Credentials are alredy taken" },
                      403: { "description": "Invalid admin password (if specified)" }
                  })
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_async_db)) -> UserInfo:
    """Register a new user."""

    try:
        return await create_user(db=db, user=user)
    except CredentialsAlreadyTaken as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except InvalidAdminPassword as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message)


@auth_router.post("/login", tags=["Login"],
                  responses={
                      400: { "description": "Invalid credentials" }
                  })
async def login(user: UserLogin, db: AsyncSession = Depends(get_async_db)) -> LoginResponse:
    """Authenticate a user and return a login response."""

    try:
        return await try_login(db=db, provided=user)
    except InvalidCredentials as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
