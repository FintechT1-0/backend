from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta, timezone


async def active_users_distribution(db: AsyncSession, since_days: int) -> dict:
    now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    start_time = now - timedelta(days=since_days)

    hourly_query = text("""
        WITH hours AS (
            SELECT generate_series(
                :start_time,
                :end_time,
                interval '1 hour'
            ) AS hour_start
        )
        SELECT
            hours.hour_start,
            COUNT(DISTINCT sessions."user") AS active_users
        FROM hours
        LEFT JOIN sessions
        ON sessions.period && tstzrange(hours.hour_start, hours.hour_start + interval '1 hour')
        GROUP BY hours.hour_start
        ORDER BY hours.hour_start;
    """)

    hourly_result = await db.execute(hourly_query, {"start_time": start_time, "end_time": now})
    hourly_data = {row.hour_start: row.active_users for row in hourly_result.fetchall()}

    country_query = text("""
        SELECT
            country,
            COUNT(DISTINCT "user") AS active_users
        FROM sessions
        WHERE period && tstzrange(:start_time, :end_time)
        GROUP BY country
    """)

    # + 1 hour since current time is truncated (e.g. 09:01:54 -> 09:00:00)
    country_result = await db.execute(country_query, {"start_time": start_time, "end_time": now + timedelta(hours=1)})
    country_data = {row.country: row.active_users for row in country_result.fetchall()}

    return {
        "distribution": hourly_data,
        "countries": country_data
    }