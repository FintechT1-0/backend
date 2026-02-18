from app.api.telemetry.schemas import (
    IPInfo, NumericalTelemetry, UserPaginationInfo,
    UserFilter, UserView, UserSuspend
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import (
    func, select, distinct,
    and_
)
from app.config.models import UserSession, Course, User 
from datetime import datetime, timedelta
from app.shared.utils import paginate
from app.api.auth.utils import get_user_by_id
from app.api.auth.errors import NonExistentUser
from app.api.telemetry.errors import CannotSuspendAnotherAdmin

import httpx


async def try_suspend_user(db: AsyncSession, parameters: UserSuspend):
    user = await get_user_by_id(db, parameters.id)

    print(f"Got user: {user}")

    if not user:
        raise NonExistentUser
    
    if user.role == "admin":
        raise CannotSuspendAnotherAdmin
    
    user.is_suspended = parameters.status

    await db.commit()



async def filter_users(db: AsyncSession, parameters: UserFilter) -> UserPaginationInfo:
    query = select(User)

    conditions = [c for c in [
        User.name == parameters.name if parameters.name is not None else None,
        User.surname == parameters.surname if parameters.surname is not None else None,
        User.email == parameters.email if parameters.email is not None else None,
        User.is_suspended == parameters.is_suspended if parameters.is_suspended is not None else None,
    ] if c is not None]

    if conditions:
        query = query.where(and_(*conditions))

    users, total_users, total_pages = await paginate(
        db=db,
        base_query=query,
        page=parameters.page,
        page_size=parameters.page_size
    )

    return UserPaginationInfo(
        users=[UserView.from_orm(user) for user in users],
        current_page=parameters.page,
        page_size=len(users),
        total_users=total_users,
        total_pages=total_pages
    )


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