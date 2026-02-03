from pydantic import BaseModel
from typing import Dict
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