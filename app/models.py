from sqlalchemy import Column, Integer, String, JSON, Float, Boolean, DateTime
from app.database import Base
from datetime import datetime
from sqlalchemy.dialects.postgresql import ARRAY



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
    title = Column(JSON, nullable=False)
    description = Column(JSON, nullable=False)
    link = Column(String, nullable=False)
    durationText = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    tags = Column(ARRAY(String), nullable=False)
    isPublished = Column(Boolean, default=False)
    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)