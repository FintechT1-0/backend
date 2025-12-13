from fastapi.testclient import TestClient
from app.main import app
from app.database import get_async_db, Base
from app.tests.utils.database import _test_get_async_db, engine
from sqlalchemy import text
import pytest
import pytest_asyncio


@pytest_asyncio.fixture(scope="session", autouse=True)
async def prepare_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="session")
def client():
    app.dependency_overrides[get_async_db] = _test_get_async_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function", autouse=True)
async def cleanup_db():
    yield
    async with engine.begin() as conn:
        for table in Base.metadata.tables.values():
            await conn.execute(text(f"DELETE FROM {table.name}"))