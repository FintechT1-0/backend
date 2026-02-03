from pydantic import BaseModel, Field, EmailStr
from typing import Optional


class EmailResend(BaseModel):
    email: EmailStr = Field(...)


class VerificationToken(BaseModel):
    token: str


class EmailCheck(BaseModel):
    email: str


class CheckResult(BaseModel):
    exists: bool


class CurrentUser(BaseModel):
    name: str
    surname: str
    email: str
    role: str
    id: int

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr = Field(...)
    password: str = Field(...)

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=40, pattern=r"^[A-ZА-ЯІЇЄҐ][A-Za-zА-Яа-яІіЇїЄєҐґ\-']{0,39}$")
    surname: str = Field(min_length=1, max_length=40, pattern=r"^[A-ZА-ЯІЇЄҐ][A-Za-zА-Яа-яІіЇїЄєҐґ\-']{0,39}$")
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    admin_password: Optional[str] = None

    class Config:
        from_attributes = True


class UserInfo(BaseModel):
    name: str
    surname: str
    email: str
    role: str

    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    token: str
    user: UserInfo