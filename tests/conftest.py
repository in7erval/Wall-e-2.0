"""
Pytest fixtures for Wall-e 2.0 tests
"""
import asyncio
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from database.models import Base
from database.repositories import UserRepository, MessageRepository


# Test database URL (in-memory SQLite for fast tests)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create event loop for tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def async_engine():
    """Create async engine for tests"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def async_session(async_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create async session for tests"""
    session_maker = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)
    async with session_maker() as session:
        yield session


@pytest_asyncio.fixture
async def user_repository(async_session: AsyncSession) -> UserRepository:
    """Create user repository for tests"""
    return UserRepository(async_session)


@pytest_asyncio.fixture
async def message_repository(async_session: AsyncSession) -> MessageRepository:
    """Create message repository for tests"""
    return MessageRepository(async_session)
