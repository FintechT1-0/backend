from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.insights.schemas import NewsItem
from app.api.auth.services import get_user, get_optional_user
from app.database import get_async_db
from app.api.auth.schemas import CurrentUser
from typing import List, Optional
from app.api.insights.services import get_filtered_articles
from app.docs import user_required


insights_router = APIRouter()


@insights_router.get("/en", tags=["Insights"], 
                     responses={
                         **user_required
                     })
async def get_en_news(
    db: AsyncSession = Depends(get_async_db),
    current_user: Optional[CurrentUser] = Depends(get_optional_user)
) -> List[NewsItem]:
    '''
    Retrieves a list of 10 insights in English.
    '''
    return await get_filtered_articles(db, "EN")


@insights_router.get("/ua", tags=["Insights"],
                     responses={
                         **user_required
                     })
async def get_ua_news(
    db: AsyncSession = Depends(get_async_db),
    current_user: Optional[CurrentUser] = Depends(get_optional_user)
) -> List[NewsItem]:
    '''
    Retrieves a list of 10 insights in Ukrainian.
    '''
    return await get_filtered_articles(db, "UA")
