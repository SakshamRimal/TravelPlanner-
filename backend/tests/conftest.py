import asyncio
from datetime import datetime, timedelta
from typing import AsyncGenerator, Generator
from uuid import uuid4

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
from sqlmodel import SQLModel, Field
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession as SASyncSession
from sqlalchemy.pool import StaticPool

from app.core.config import Settings
from app.db.session import get_session
from app.main import app
from backend.app.models.user_model import User
from backend.app.models.trip_model import Trip
from backend.app.models.refreshtoken_model import RefreshToken
from app.core.security import get_password_hash, create_access_token


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def test_engine():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSession(test_engine) as session:
        yield session


@pytest_asyncio.fixture
async def test_user(test_session: AsyncSession) -> User:
    user = User(
        id=uuid4(),
        email="test@example.com",
        full_name="Test User",
        hashed_password=get_password_hash("TestPass123"),
        is_active=True,
    )
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def other_user(test_session: AsyncSession) -> User:
    user = User(
        id=uuid4(),
        email="other@example.com",
        full_name="Other User",
        hashed_password=get_password_hash("OtherPass123"),
        is_active=True,
    )
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user: User) -> dict:
    token = create_access_token(str(test_user.id))
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def other_user_headers(other_user: User) -> dict:
    token = create_access_token(str(other_user.id))
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def sample_trip(test_session: AsyncSession, test_user: User) -> Trip:
    trip = Trip(
        id=uuid4(),
        user_id=test_user.id,
        origin="KTM",
        destination="Pokhara",
        budget=50000,
        travelers=2,
        start_date=datetime.now().date() + timedelta(days=7),
        end_date=datetime.now().date() + timedelta(days=10),
        status="planned",
    )
    test_session.add(trip)
    await test_session.commit()
    await test_session.refresh(trip)
    return trip


@pytest_asyncio.fixture
async def async_client(test_session: AsyncSession, test_engine) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
        yield test_session

    app.dependency_overrides[get_session] = override_get_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()