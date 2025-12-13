from pydantic import BaseModel, Field, validator, HttpUrl
from typing import List, Optional, Literal
from datetime import datetime


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


class CourseCreate(BaseModel):
    title: str = Field(..., max_length=256)
    description: str = Field(..., max_length=2048)
    link: HttpUrl
    durationText: str = Field(..., min_length=0, max_length=64)
    price: float = Field(..., ge=0)
    tags: List[str] = Field(default_factory=list)
    isPublished: bool = False
    lang: Literal["EN", "UA"]

    @validator('tags', pre=True, always=True)
    def validate_tags(cls, v):
        return tags_validator(v)


class CourseUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=256)
    description: Optional[str] = Field(None, max_length=2048)
    link: Optional[HttpUrl]
    durationText: Optional[str] = Field(None, min_length=0, max_length=64)
    price: Optional[float] = Field(None, ge=0)
    tags: Optional[List[str]] = None
    isPublished: Optional[bool] = None
    lang: Optional[Literal["EN", "UA"]] = None

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