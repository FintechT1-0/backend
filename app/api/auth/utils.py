from passlib.context import CryptContext
from datetime import datetime, timedelta
from app.api.auth.errors import ExpiredToken, InvalidToken
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.config.models import User
from app.config.environment import settings
from loguru import logger
import jwt


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).filter(User.email == email))
    return result.scalars().first()


def hash_password(password: str) -> str:
    logger.debug(f"Hashing password {password}")
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise ExpiredToken
    except jwt.PyJWTError as e:
        logger.debug(f"JWT error: {str(e)}")
        raise InvalidToken