from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.insights.schemas import NewsItem
from app.auth.services import get_user
from app.database import get_async_db
from app.auth.schemas import CurrentUser
from typing import List
from app.insights.services import get_filtered_articles


insights_router = APIRouter()


@insights_router.get("/en")
async def get_en_news(
    db: AsyncSession = Depends(get_async_db),
    current_user: CurrentUser = Depends(get_user)
) -> List[NewsItem]:
    return await get_filtered_articles(db, "EN")


@insights_router.get("/ua")
async def get_ua_news(
    db: AsyncSession = Depends(get_async_db),
    current_user: CurrentUser = Depends(get_user)
) -> List[NewsItem]:
    return await get_filtered_articles(db, "UA")
