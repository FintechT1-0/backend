from sqlalchemy import Column, Integer, String, JSON, Float, Boolean, DateTime, Text
from app.database import Base
from datetime import datetime
from sqlalchemy.dialects.postgresql import ARRAY


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, nullable=False)
    thumbnail = Column(String, nullable=False)
    image = Column(String, nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    date = Column(String, nullable=False)
    excerpt = Column(Text, nullable=False)
    lang = Column(String, nullable=False)
    category = Column(String, nullable=False)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    role = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)

    title_ua = Column(String, nullable=False)
    title_en = Column(String, nullable=False)

    description_ua = Column(String, nullable=False)
    description_en = Column(String, nullable=False)

    link = Column(String, nullable=True)
    speaker = Column(String, nullable=True)
    image = Column(String, nullable=True)

    category = Column(String, nullable=False)
    tags = Column(ARRAY(String), nullable=False)

    durationText = Column(String, nullable=False)

    price = Column(Float, nullable=False)

    isPublished = Column(Boolean, default=False, nullable=False)
    createdAt = Column(DateTime, default=datetime.utcnow, nullable=False)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)