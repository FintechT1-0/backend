from app.api.telemetry.schemas import IPInfo, NumericalTelemetry
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import (
    func, select, distinct
)
from app.config.models import UserSession, Course, User 
from datetime import datetime, timedelta
import httpx


async def fetch_ip_info(ip: str) -> IPInfo:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://ipinfo.io/{ip}/json")
        response.raise_for_status()
        data = response.json()

    return IPInfo(**data)


async def save_record(db: AsyncSession, start: datetime, end: datetime, ip: str, country: str, user: int):
    db_record = UserSession(period=(start, end), country=country, ip=ip, user=user)
    db.add(db_record)
    await db.commit()


async def get_numerical_telemetry(db: AsyncSession) -> NumericalTelemetry:
    courses_count_query = select(func.count()).select_from(Course)
    result = await db.execute(courses_count_query)
    courses_count = result.scalar_one()

    users_count_query = select(func.count()).select_from(User)
    result = await db.execute(users_count_query)
    users_count = result.scalar_one()
    
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)

    active_users_query = (
        select(func.count(distinct(UserSession.user)))
        .where(UserSession.period.op('&&')(func.tstzrange(thirty_days_ago, func.now())))
    )

    result = await db.execute(active_users_query)
    active_users_count = result.scalar_one()

    return NumericalTelemetry(
        total_users=users_count,
        active_users=active_users_count,
        total_courses=courses_count
    )