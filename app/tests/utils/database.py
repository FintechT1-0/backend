from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from app.tests.utils.environment import settings


engine = create_async_engine(
    settings.TEST_DATABASE_URL,
    echo=False,
    future=True,
    poolclass=NullPool
)


_TestAsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def _test_get_async_db():
    async with _TestAsyncSessionLocal() as session:
        yield session