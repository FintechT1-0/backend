from pydantic import BaseModel, Field, HttpUrl, validator
from typing import List, Optional
from datetime import datetime


url_pattern = r'^(https?://)?(www\.)?[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}(/[-a-zA-Z0-9%_&?=]*)?$'


def tags_validator(tags: List[str]) -> List[str]:
    if tags is not None:
        normalized_tags = [tag.strip().lower() for tag in tags]
        normalized_tags = list(set(normalized_tags))

        if len(tags) == 0:
            raise ValueError("Specify at least 1 tag")
        
        if len(tags) > 10:
            raise ValueError("No more than 10 tags")
        
        for tag in tags:
            if len(tag) > 50:
                raise ValueError("Each tag cannot be longer than 50 characters")
            
        return normalized_tags
    return tags


class LangField(BaseModel):
    ua: str = Field(None, max_length=256)
    en: str = Field(None, max_length=256)

    @validator('*', pre=True, always=True)
    def not_empty(cls, v):
        if v is not None and not v.strip():
            raise ValueError("This field cannot be empty")
        return v


class LongLangField(BaseModel):
    ua: str = Field(None, max_length=2048)
    en: str = Field(None, max_length=2048)

    @validator('*', pre=True, always=True)
    def not_empty(cls, v):
        if v is not None and not v.strip():
            raise ValueError("This field cannot be empty")
        return v


class CourseCreate(BaseModel):
    title: LangField
    description: LongLangField
    link: str = Field(..., pattern=url_pattern)
    durationText: str = Field(..., min_length=1, max_length=64)
    price: float = Field(..., ge=0)
    tags: List[str] = Field(default_factory=list)
    isPublished: bool = False

    @validator('tags', pre=True, always=True)
    def validate_tags(cls, v):
        return tags_validator(v)


class CourseUpdate(BaseModel):
    title: Optional[LangField] = None
    description: Optional[LangField] = None
    link: Optional[str] = Field(None, pattern=url_pattern)
    durationText: Optional[str] = Field(None, min_length=1, max_length=64)
    price: Optional[float] = Field(None, ge=0)
    tags: Optional[List[str]] = None
    isPublished: Optional[bool] = None

    @validator('tags', pre=True, always=True)
    def validate_tags(cls, v):
        return tags_validator(v)


class CourseView(CourseCreate):
    id: int
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True


class PaginationInfo(BaseModel):
    courses: List[CourseView]
    current_page: int
    page_size: int
    total_courses: int
    total_pages: int