from pydantic import BaseModel, Field, validator, HttpUrl
from typing import List, Optional
from datetime import datetime
from fastapi import Query


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
    title_ua: str = Field(..., min_length=1, max_length=256)
    title_en: str = Field(..., min_length=1, max_length=256)

    description_ua: str = Field(..., min_length=1, max_length=2048)
    description_en: str = Field(..., min_length=1, max_length=2048)

    category: str = Field(..., min_length=1, max_length=128)

    tags: List[str] = Field(..., min_items=1)

    durationText: str = Field(..., min_length=1, max_length=64)

    price: float = Field(..., ge=0)

    link: Optional[HttpUrl] = None
    speaker: Optional[str] = Field(None, min_length=1, max_length=256)
    image: Optional[str] = Field(None, min_length=1, max_length=512)

    isPublished: bool = False

    @validator("tags", pre=True)
    def validate_tags(cls, v):
        return tags_validator(v)


class CourseUpdate(BaseModel):
    title_ua: Optional[str] = Field(None, min_length=1, max_length=256)
    title_en: Optional[str] = Field(None, min_length=1, max_length=256)

    description_ua: Optional[str] = Field(None, min_length=1, max_length=2048)
    description_en: Optional[str] = Field(None, min_length=1, max_length=2048)

    category: Optional[str] = Field(None, min_length=1, max_length=128)

    tags: Optional[List[str]] = None

    durationText: Optional[str] = Field(None, min_length=1, max_length=64)

    price: Optional[float] = Field(None, ge=0)

    link: Optional[HttpUrl] = None
    speaker: Optional[str] = Field(None, min_length=1, max_length=256)
    image: Optional[str] = Field(None, min_length=1, max_length=512)

    isPublished: Optional[bool] = None

    @validator("tags", pre=True)
    def validate_tags(cls, v):
        return tags_validator(v)
    

class CourseFilter(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

    category: Optional[str] = None
    
    durationText: Optional[str] = None

    price_min: Optional[float] = Field(None, ge=0)
    price_max: Optional[float] = Field(None, ge=0)

    link: Optional[str] = None
    speaker: Optional[str] = None
    image: Optional[str] = None
    
    isPublished: Optional[bool] = None

    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)


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


class CourseId(BaseModel):
    id: int