from pydantic import BaseModel
from datetime import datetime


class IPInfo(BaseModel):
    country: str


class Record(BaseModel):
    ip: str
    start: datetime
    end: datetime
    country: str