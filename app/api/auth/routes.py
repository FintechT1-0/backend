from fastapi import (
    APIRouter, Depends, HTTPException, 
    status, BackgroundTasks, Response
)
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.auth.schemas import (
    CurrentUser, UserLogin, UserCreate, 
    UserInfo, LoginResponse, EmailCheck, 
    CheckResult, VerificationToken, EmailResend
)
from app.api.auth.services import (
    get_user, try_login, create_user, 
    check_email, send_email_async, try_verify_email
)
from app.api.auth.utils import create_access_token 
from app.database import get_async_db
from app.api.auth.errors import (
    InvalidCredentials, CredentialsAlreadyTaken, InvalidAdminPassword,
    UnverifiedEmail, ExpiredToken, InvalidToken, NonExistentUser
)
from app.docs import user_required, either


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
                      400: { "description": CredentialsAlreadyTaken.message },
                      403: { "description": InvalidAdminPassword.message }
                  })
async def register_user(
    user: UserCreate, 
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_async_db),
) -> UserInfo:
    """Register a new user."""

    try:
        user_info = await create_user(db=db, user=user)
        v_token = create_access_token({"sub": user_info.email})
        background_tasks.add_task(send_email_async, recipient=user_info.email, verification_token=v_token)

        return user_info

    except CredentialsAlreadyTaken as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except InvalidAdminPassword as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message)


@auth_router.post("/login", tags=["Login"],
                  responses={
                      400: { "description": InvalidCredentials.message },
                      403: { "description": UnverifiedEmail.message }
                  })
async def login(user: UserLogin, db: AsyncSession = Depends(get_async_db)) -> LoginResponse:
    """Authenticate a user and return a login response."""

    try:
        return await try_login(db=db, provided=user)
    except InvalidCredentials as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except UnverifiedEmail as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message)


@auth_router.post("/verify", tags=["Verification"],
                  responses={
                      204: { "description": "Successful verification." },
                      403: { "description": either(ExpiredToken.message, InvalidToken.message, NonExistentUser.message) }
                  })
async def verify_email(token: VerificationToken, db: AsyncSession = Depends(get_async_db)) -> Response:
    """Verify your email by JWT token."""
    try:
        await try_verify_email(db, token)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except (ExpiredToken, InvalidToken, NonExistentUser) as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message)
    

@auth_router.post("/resend", tags=["Verification"],
                  responses={
                      204: { "description": "Task to send a letter initiated successfully." }
                  })
async def resend_email(email: EmailResend, background_tasks: BackgroundTasks) -> Response:
    """Resend a letter to verify your email."""
    v_token = create_access_token({"sub": email.email})
    background_tasks.add_task(send_email_async, recipient=email.email, verification_token=v_token, resend=True)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

    
    



