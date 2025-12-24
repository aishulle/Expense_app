import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
import asyncio
from uuid import uuid4

from app.core.database import Base, get_db
from app.models import User, Group, GroupMember
from app.main import app


# Test database URL (in-memory SQLite for testing)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture(scope="function")
async def db_session():
    """Create a test database session."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestSessionLocal() as session:
        yield session
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
def override_get_db(db_session):
    """Override the get_db dependency."""
    async def _get_db():
        yield db_session
    return _get_db


@pytest.fixture
async def mock_redis():
    """Mock Redis client for testing."""
    from unittest.mock import AsyncMock
    mock_redis = AsyncMock()
    mock_redis.get = AsyncMock(return_value=None)
    mock_redis.setex = AsyncMock(return_value=True)
    mock_redis.delete = AsyncMock(return_value=0)
    return mock_redis


@pytest.fixture
async def client(override_get_db, mock_redis):
    """Create a test client."""
    from app.core.redis_client import get_redis
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_redis] = lambda: mock_redis
    from httpx import AsyncClient
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture
async def test_user(db_session: AsyncSession):
    """Create a test user."""
    user = User(id=uuid4(), name="Test User", email="test@example.com")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_users(db_session: AsyncSession):
    """Create multiple test users."""
    users = []
    for i in range(3):
        user = User(
            id=uuid4(),
            name=f"User {i+1}",
            email=f"user{i+1}@example.com"
        )
        db_session.add(user)
        users.append(user)
    await db_session.commit()
    for user in users:
        await db_session.refresh(user)
    return users


@pytest.fixture
async def test_group(db_session: AsyncSession, test_user):
    """Create a test group with one member."""
    group = Group(id=uuid4(), name="Test Group")
    db_session.add(group)
    await db_session.flush()
    
    member = GroupMember(group_id=group.id, user_id=test_user.id)
    db_session.add(member)
    await db_session.commit()
    await db_session.refresh(group)
    return group

