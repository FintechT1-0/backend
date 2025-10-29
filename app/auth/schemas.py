from pydantic import BaseModel, Field, EmailStr


class EmailCheck(BaseModel):
    email: str


class CheckResult(BaseModel):
    exists: bool


class CurrentUser(BaseModel):
    name: str
    surname: str
    email: str
    id: int

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr = Field(...)
    password: str = Field(...)

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=40, pattern=r'^[A-Z][a-z]{0,39}$')
    surname: str = Field(min_length=1, max_length=40, pattern=r'^[A-Z][a-z]{0,39}$')
    email: EmailStr = Field(...)
    password: str = Field(..., min_length=8, max_length=128)

    class Config:
        from_attributes = True


class UserInfo(BaseModel):
    name: str
    surname: str
    email: str

    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    token: str
    user: UserInfo