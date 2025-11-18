from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.auth.schemas import (
    UserCreate, UserLogin, CurrentUser, 
    LoginResponse, UserInfo, EmailCheck, 
    CheckResult
)
from app.auth.utils import hash_password
from app.models import User
from app.auth.utils import (
    verify_password, create_access_token, decode_access_token, 
    get_user_by_email
)
from app.auth.errors import (
    InvalidCredentials, CredentialsAlreadyTaken, InvalidToken, 
    ExpiredToken, NonExistentUser, InvalidAdminPassword
)
from app.database import get_async_db
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from loguru import logger
from app.main import settings
import time


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def check_email(data: EmailCheck, db: AsyncSession) -> CheckResult:
    exists = True if await get_user_by_email(db, data.email) else False
    return CheckResult(exists=exists)


async def get_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_async_db)) -> CurrentUser:
    try:
        user = await get_user_by_token(token, db)
        logger.debug(user)
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

    t1 = time.perf_counter()
    result = await db.execute(select(User).filter(User.email == email))
    t2 = time.perf_counter()
    user = result.scalars().first()
    t3 = time.perf_counter()

    print(f"db query: {t2 - t1}, scalars/fetch: {t3 - t2}")

    '''
    t0 = time.perf_counter()
    result = await db.execute(select(User).filter(User.email == email))
    print("query:", (time.perf_counter() - t0) * 1000, "ms")
    user = result.scalars().first()
    '''
    
    if not user:
        raise NonExistentUser
    
    return CurrentUser(name=user.name, surname=user.surname, email=user.email, role=user.role, id=user.id)


async def try_login(db: AsyncSession, provided: UserLogin) -> LoginResponse:
    logger.debug(f"Trying to log in, user = {provided}")
    user = await get_user_by_email(db, provided.email)

    if not user or not verify_password(provided.password, user.hashed_password):
        raise InvalidCredentials
    
    access_token = create_access_token(data={"sub": user.email})

    return LoginResponse(token=access_token, user=user)


async def create_user(db: AsyncSession, user: UserCreate) -> UserInfo:
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

    return UserInfo(name=db_user.name, surname=db_user.surname, email=db_user.email, role=db_user.role)
