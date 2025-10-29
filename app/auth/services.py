from sqlalchemy.orm import Session
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
    ExpiredToken, NonExistentUser
)
from app.database import get_db
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from loguru import logger


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def check_email(data: EmailCheck, db: Session) -> CheckResult:
    return CheckResult(exists=(True if get_user_by_email(db, data.email) else False))


def get_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> CurrentUser:
    try:
        user = get_user_by_token(token, db)
        logger.debug(user)
    except (ExpiredToken, InvalidToken) as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=e.message)
    except NonExistentUser as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    
    return user


def get_user_by_token(token: str, db: Session) -> CurrentUser:
    payload = decode_access_token(token)
    email = payload.get("sub")

    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        raise NonExistentUser
    
    return CurrentUser(name=user.name, surname=user.surname, email=user.email, id = user.id)


def try_login(db: Session, provided: UserLogin) -> LoginResponse:
    logger.debug(f"Trying to log in, user = {provided}")
    user = get_user_by_email(db, provided.email)

    if not user or (user and not verify_password(provided.password, user.hashed_password)):
        raise InvalidCredentials
    
    access_token = create_access_token(data={"sub": user.email})

    return LoginResponse(token=access_token, user=user)


def create_user(db: Session, user: UserCreate) -> UserInfo:
    existing_user = get_user_by_email(db, user.email)

    if existing_user:
        raise CredentialsAlreadyTaken
    
    db_user = User(
        name = user.name,
        surname = user.surname,
        email = user.email,
        hashed_password = hash_password(user.password)
    )

    db.add(db_user)
    db.commit()

    return UserInfo(name=user.name, surname=user.surname, email=user.email)