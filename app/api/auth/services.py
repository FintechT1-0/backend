from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.api.auth.schemas import (
    UserCreate, UserLogin, CurrentUser, 
    LoginResponse, UserInfo, EmailCheck, 
    CheckResult
)
from app.config.models import User
from app.api.auth.utils import (
    verify_password, create_access_token, decode_access_token, 
    get_user_by_email, hash_password
)
from app.api.auth.errors import (
    InvalidCredentials, CredentialsAlreadyTaken, InvalidToken, 
    ExpiredToken, NonExistentUser, InvalidAdminPassword,
    UnverifiedEmail
)
from app.config.database import get_async_db
from fastapi import (
    Depends, HTTPException, status,
    WebSocket, BackgroundTasks
)
from fastapi.security import OAuth2PasswordBearer
from loguru import logger
from app.config.environment import settings
from typing import Optional
from app.config.template_storage import templates
from datetime import datetime
import httpx


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


async def get_current_user_ws(
    websocket: WebSocket,
    db: AsyncSession = Depends(get_async_db),
) -> CurrentUser:
    token = websocket.query_params.get("token")

    if not token:
        return "Missing token."

    try:
        return await get_user_by_token(token, db)
    except (ExpiredToken, InvalidToken, NonExistentUser) as e:
        return e.message


async def check_email(data: EmailCheck, db: AsyncSession) -> CheckResult:
    exists = True if await get_user_by_email(db, data.email) else False
    return CheckResult(exists=exists)


async def get_optional_user(
    token: Optional[str] = Depends(oauth2_scheme_optional), 
    db: AsyncSession = Depends(get_async_db)
) -> Optional[CurrentUser]:
    if token is None:
        return None

    try:
        return await get_user_by_token(token, db)
    except (ExpiredToken, InvalidToken, NonExistentUser):
        return None


async def get_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_async_db)) -> CurrentUser:
    try:
        user = await get_user_by_token(token, db)
    except (ExpiredToken, InvalidToken) as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=e.message)
    except NonExistentUser as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    
    return user


async def get_admin(current_user: CurrentUser = Depends(get_user)) -> CurrentUser:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied."
        )
    return current_user


async def get_user_by_token(token: str, db: AsyncSession) -> CurrentUser:
    payload = decode_access_token(token)
    email = payload.get("sub")

    result = await db.execute(select(User).filter(User.email == email))
    user = result.scalars().first()

    if not user:
        raise NonExistentUser
    
    return CurrentUser(name=user.name, surname=user.surname, email=user.email, role=user.role, id=user.id)


async def try_login(db: AsyncSession, provided: UserLogin) -> LoginResponse:
    logger.debug(f"Trying to log in, user = {provided}")
    user = await get_user_by_email(db, provided.email)

    if not user or not verify_password(provided.password, user.hashed_password):
        raise InvalidCredentials
    
    if user.is_verified == False:
        raise UnverifiedEmail
    
    access_token = create_access_token(data={"sub": user.email})

    return LoginResponse(token=access_token, user=user)


async def create_user(db: AsyncSession, tasks: BackgroundTasks, user: UserCreate) -> UserInfo:
    existing_user = await get_user_by_email(db, user.email)

    if existing_user:
        raise CredentialsAlreadyTaken

    if user.admin_password:
        if user.admin_password == settings.ADMIN_PASSWORD:
            role = "admin"
        else:
            raise InvalidAdminPassword
    else:
        role = "user"

    db_user = User(
        name=user.name,
        surname=user.surname,
        email=user.email,
        hashed_password=hash_password(user.password),
        role=role
    )

    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    await initiate_verification_task(tasks, user.email)

    return UserInfo(name=db_user.name, surname=db_user.surname, email=db_user.email, role=db_user.role)


async def initiate_verification_task(tasks: BackgroundTasks, recipient: str):
    verification_token = create_access_token({"sub": recipient})
    tasks.add_task(
        send_email_async,
        recipient=recipient,
        template_name='verify',
        template_args={
            "verification_link": settings.BACKEND_URL + f"/auth/verify?token={verification_token}",
            "year": str(datetime.now().year)
        },
        subject="Email verification"
    )


async def send_email_async(recipient: str, template_name: str, template_args: dict, subject: str):
    payload = {
        "from": settings.EMAIL,
        "to": [recipient],
        "subject": subject,
        "html": templates[template_name].render(**template_args)
    }

    logger.debug(f"Sending letter f'{template_name}.html' with arguments: {template_args}")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://www.unosend.co/api/v1/emails", 
                headers={"Authorization": f"Bearer {settings.UNOSEND_API_KEY}"}, 
                json=payload
            )
            response.raise_for_status()
    except Exception as e:
        logger.critical(f"Critial error while sending a letter: {str(e)}")


async def try_verify_email(db: AsyncSession, token: str):
    payload = decode_access_token(token)
    email = payload.get("sub")

    user = await get_user_by_email(db, email)

    if not user:
        raise NonExistentUser

    user.is_verified = True

    db.add(user)
    await db.commit()



