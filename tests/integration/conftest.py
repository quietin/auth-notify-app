
import pytest_asyncio
from sqlmodel import SQLModel, create_engine, Session
from app.database import get_session
from app.main import app
from httpx import AsyncClient, ASGITransport
from sqlalchemy.pool import StaticPool

# Create a shared in-memory SQLite engine for testing
test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
# Automatically reset the database schema before each test
@pytest_asyncio.fixture(scope="function", autouse=True)
def setup_database():
    SQLModel.metadata.drop_all(test_engine)
    SQLModel.metadata.create_all(test_engine)

# Provide an HTTPX AsyncClient with FastAPI app and session override
@pytest_asyncio.fixture(scope="function")
async def client():
    def override_get_session():
        with Session(test_engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
