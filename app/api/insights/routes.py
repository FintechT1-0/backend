from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.insights.schemas import NewsItem
from app.api.auth.services import get_user
from app.database import get_async_db
from app.api.auth.schemas import CurrentUser
from typing import List
from app.api.insights.services import get_filtered_articles


insights_router = APIRouter()


@insights_router.get("/en", tags=["Insights"])
async def get_en_news(
    db: AsyncSession = Depends(get_async_db),
    current_user: CurrentUser = Depends(get_user)
) -> List[NewsItem]:
    return await get_filtered_articles(db, "EN")


@insights_router.get("/ua", tags=["Insights"])
async def get_ua_news(
    db: AsyncSession = Depends(get_async_db),
    current_user: CurrentUser = Depends(get_user)
) -> List[NewsItem]:
    return await get_filtered_articles(db, "UA")
