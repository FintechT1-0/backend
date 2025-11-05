from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.auth.schemas import (
    CurrentUser, UserLogin, UserCreate, 
    UserInfo, LoginResponse, EmailCheck, 
    CheckResult
)
from app.auth.services import (
    get_user, try_login, create_user, 
    check_email
)
from app.database import get_db
from app.auth.errors import (
    InvalidCredentials, CredentialsAlreadyTaken, InvalidAdminPassword
)


auth_router = APIRouter()


@auth_router.post("/checkEmail")
def check_existing_email(data: EmailCheck, db: Session = Depends(get_db)) -> CheckResult:
    """Check if an email is already registered."""

    return check_email(data, db)


@auth_router.get("/me")
def get_me(current_user: CurrentUser = Depends(get_user)) -> UserInfo:
    """Retrieve the currently authenticated user by token."""

    return current_user


@auth_router.post("/register")
def register_user(user: UserCreate, db: Session = Depends(get_db)) -> UserInfo:
    """Register a new user."""

    try:
        return create_user(db=db, user=user)
    except CredentialsAlreadyTaken as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except InvalidAdminPassword as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message)


@auth_router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)) -> LoginResponse:
    """Authenticate a user and return a login response."""

    try:
        return try_login(db=db, provided=user)
    except InvalidCredentials as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
