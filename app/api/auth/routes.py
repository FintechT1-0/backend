from fastapi import (
    APIRouter, Depends, HTTPException, 
    status, BackgroundTasks, Response,
    Query
)
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.auth.schemas import (
    CurrentUser, UserLogin, UserCreate, 
    UserInfo, LoginResponse, EmailCheck, 
    CheckResult, EmailResend
)
from app.api.auth.services import (
    get_user, try_login, create_user, 
    check_email, try_verify_email, initiate_verification_task
)
from app.config.database import get_async_db
from app.api.auth.errors import (
    InvalidCredentials, CredentialsAlreadyTaken, InvalidAdminPassword,
    UnverifiedEmail, ExpiredToken, InvalidToken, NonExistentUser
)
from app.config.docs import user_required, either
from app.config.environment import settings
import json


auth_router = APIRouter()


@auth_router.post("/checkEmail", tags=["Registration"])
async def check_existing_email(data: EmailCheck, db: AsyncSession = Depends(get_async_db)) -> CheckResult:
    """Check if an email is already registered."""

    return await check_email(data, db)


@auth_router.get("/me", tags=["Info"],
                 responses={
                     **user_required
                 })
async def get_me(current_user: CurrentUser = Depends(get_user)) -> UserInfo:
    """Retrieve the currently authenticated user by token."""

    return current_user


@auth_router.post("/register", tags=["Registration"],
                  responses={
                      400: { "description": CredentialsAlreadyTaken.message['en'] },
                      403: { "description": InvalidAdminPassword.message['en'] }
                  })
async def register_user(
    user: UserCreate, 
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_async_db),
) -> UserInfo:
    """Register a new user."""

    try:
        return await create_user(db, background_tasks, user)

    except CredentialsAlreadyTaken as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except InvalidAdminPassword as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message)


@auth_router.post("/login", tags=["Login"],
                  responses={
                      400: { "description": InvalidCredentials.message['en'] },
                      403: { "description": UnverifiedEmail.message['en'] }
                  })
async def login(user: UserLogin, db: AsyncSession = Depends(get_async_db)) -> LoginResponse:
    """Authenticate a user and return a login response."""

    try:
        return await try_login(db=db, provided=user)
    except InvalidCredentials as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except UnverifiedEmail as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message)


@auth_router.get("/verify", tags=["Verification"],
                  responses={
                      204: { "description": "Successful verification." },
                      403: { "description": either(ExpiredToken.message['en'], InvalidToken.message['en'], NonExistentUser.message['en']) }
                  })
async def verify_email(token: str = Query(...), db: AsyncSession = Depends(get_async_db)) -> RedirectResponse:
    """Verify your email by JWT token."""
    try:
        await try_verify_email(db, token)

        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/login?verification=true",
            status_code=status.HTTP_302_FOUND
        )
    
    except (ExpiredToken, InvalidToken, NonExistentUser) as e:
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/login?verification=false&reason={json.dumps(e.message)}",
            status_code=status.HTTP_302_FOUND
        )
    

@auth_router.post("/resend", tags=["Verification"],
                  responses={
                      204: { "description": "Task to send a letter initiated successfully." }
                  })
async def resend_email(email: EmailResend, background_tasks: BackgroundTasks) -> Response:
    """Resend a letter to verify your email."""
    await initiate_verification_task(background_tasks, email.email)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

    
    



