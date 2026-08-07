from collections.abc import AsyncGenerator, Iterator

import pytest
import pytest_asyncio
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from testcontainers.community.postgres import PostgresContainer


@pytest.fixture(scope="session")
def postgres_container() -> Iterator[PostgresContainer]:
    """
    Spins up a real TimescaleDB container for the entire test session.
    Runs Alembic migrations once for the session.
    """
    with PostgresContainer("timescale/timescaledb:latest-pg14", driver="asyncpg") as postgres:
        database_url = postgres.get_connection_url()

        # We must configure Alembic to use the testcontainer's database URL.
        alembic_cfg = Config("alembic.ini")
        alembic_cfg.set_main_option("sqlalchemy.url", database_url)

        # Run 'upgrade head'. command.upgrade will internally use asyncio.run()
        # Since this is a synchronous fixture, this is perfectly safe.
        command.upgrade(alembic_cfg, "head")

        yield postgres


@pytest_asyncio.fixture
async def db_engine(postgres_container: PostgresContainer) -> AsyncGenerator[AsyncEngine, None]:
    """
    Creates an async SQLAlchemy engine connected to the Testcontainers DB.
    Function-scoped to prevent 'attached to a different loop' errors in asyncpg.
    """
    database_url = postgres_container.get_connection_url()
    engine = create_async_engine(database_url, echo=False)

    yield engine

    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    """
    Provides a transactional database session for tests.
    """
    TestingSessionLocal = async_sessionmaker(bind=db_engine, autocommit=False, autoflush=False)
    async with TestingSessionLocal() as session:
        yield session


@pytest.fixture
def integration_client(db_session: AsyncSession) -> Iterator[TestClient]:
    """
    Provides a FastAPI TestClient with the database session dependency overridden
    to use the testcontainers database. Use this fixture for API integration tests.
    """
    from fastapi.testclient import TestClient
    from src.api.main import app
    from src.db.session import get_db_session

    async def override_get_db_session() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db_session] = override_get_db_session
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
