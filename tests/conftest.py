import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from backend.clone_twitter import app
from backend.conf import Base, get_session
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine_test = create_async_engine(TEST_DATABASE_URL, echo=True, future=True)
async_session_test = async_sessionmaker(engine_test, expire_on_commit=False)

@pytest_asyncio.fixture(scope="session")
async def init_db():
    # создаём таблицы
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine_test.dispose()


@pytest_asyncio.fixture
async def session(init_db):
    async with async_session_test() as s:
        yield s


@pytest_asyncio.fixture
async def client(session):
    app.dependency_overrides[get_session] = lambda: session

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac