from sqlalchemy.orm import Session
from app.models import Article


def get_filtered_articles(db: Session, lang: str) -> list[Article]:
    return db.query(Article).filter(Article.lang == lang).all()