from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.insights.schemas import NewsItem
from app.auth.services import get_user
from app.database import get_db
from app.auth.schemas import CurrentUser
from typing import List
from app.insights.services import get_filtered_articles


insights_router = APIRouter()


@insights_router.get("/en")
def get_en_news(db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_user)) -> List[NewsItem]:
    return get_filtered_articles(db, "EN")


@insights_router.get("/ua")
def get_en_news(db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_user)) -> List[NewsItem]:
    return get_filtered_articles(db, "UA")
