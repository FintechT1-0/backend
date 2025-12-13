from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from app.environment import settings


engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True,
    pool_size=8,
    max_overflow=0
)


AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


Base = declarative_base()


async def get_async_db():
    async with AsyncSessionLocal() as session:
        yield session