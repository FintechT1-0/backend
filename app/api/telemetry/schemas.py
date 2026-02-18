from pydantic import BaseModel, Field
from typing import Dict, Optional, List
from datetime import datetime


class IPInfo(BaseModel):
    country: str


class Distribution(BaseModel):
    distribution: Dict[datetime, int]
    countries: Dict[str, int]


class NumericalTelemetry(BaseModel):
    total_users: int
    active_users: int
    total_courses: int


class UserFilter(BaseModel):
    name: Optional[str] = None
    surname: Optional[str] = None
    email: Optional[str] = None
    is_suspended: Optional[bool] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)


class UserView(BaseModel):
    id: int
    name: str
    surname: str
    email: str
    is_suspended: bool

    class Config:
        from_attributes = True


class UserPaginationInfo(BaseModel):
    users: List[UserView]
    current_page: int
    page_size: int
    total_users: int
    total_pages: int

    class Config:
        from_attributes = True
    

class UserSuspend(BaseModel):
    status: bool
    id: int