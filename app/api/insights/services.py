from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.config.models import Article


async def get_filtered_articles(db: AsyncSession, lang: str) -> list[Article]:
    result = await db.execute(
        select(Article).where(Article.lang == lang)
    )
    return result.scalars().all()