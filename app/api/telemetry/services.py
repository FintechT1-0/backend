from app.api.telemetry.schemas import IPInfo, Record
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import UserSession
import httpx


async def fetch_ip_info(ip: str) -> IPInfo:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://ipinfo.io/{ip}/json")
        response.raise_for_status()
        data = response.json()

    return IPInfo(**data)


async def save_record(db: AsyncSession, record: Record):
    db_record = UserSession(**record.model_dump(mode="python"))
    db.add(db_record)
    await db.commit()