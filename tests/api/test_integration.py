import asyncio
from collections.abc import AsyncGenerator
from datetime import UTC, datetime

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool
from src.api.main import app
from src.db.models import OHLCVModel
from src.db.session import get_db_session
from testcontainers.community.postgres import PostgresContainer


def make_test_client(db_url: str) -> tuple[TestClient, AsyncEngine]:
    """
    Creates a FastAPI TestClient with the DB dependency overridden.
    Uses NullPool so that each request creates a fresh asyncpg connection
    within anyio's event loop — avoiding "attached to a different loop" errors.
    """
    engine = create_async_engine(db_url, echo=False, poolclass=NullPool)
    TestingSession = async_sessionmaker(bind=engine, autocommit=False, autoflush=False)

    async def override_get_db_session() -> AsyncGenerator[AsyncSession, None]:
        async with TestingSession() as session:
            yield session

    app.dependency_overrides[get_db_session] = override_get_db_session
    client = TestClient(app)
    return client, engine


async def _insert(db_url: str, rows: list[OHLCVModel]) -> None:
    """
    Opens a fresh engine+session (NullPool) to insert rows, then disposes.
    The engine is created and disposed entirely within this coroutine,
    so there's no connection leaking to another event loop.
    """
    engine = create_async_engine(db_url, echo=False, poolclass=NullPool)
    async with async_sessionmaker(bind=engine, autocommit=False, autoflush=False)() as session:
        for row in rows:
            session.add(row)
        await session.commit()
    await engine.dispose()


def insert_sync(db_url: str, rows: list[OHLCVModel]) -> None:
    """Synchronous wrapper around _insert, safe to call before TestClient.get()."""
    asyncio.run(_insert(db_url, rows))


def test_ohlcv_history_integration(postgres_container: PostgresContainer) -> None:
    """
    End-to-End integration test for the OHLCV history endpoint.
    Inserts a real record into the ephemeral testcontainers DB,
    then calls the REST endpoint and asserts the response.
    """
    db_url = postgres_container.get_connection_url()
    client, engine = make_test_client(db_url)

    try:
        # 1. Insert data using a fresh, self-contained engine (NullPool, fully disposed)
        timestamp = datetime(2024, 1, 1, 12, 0, tzinfo=UTC)
        candle = OHLCVModel(
            symbol="BTC-USDT",
            timestamp=timestamp,
            open=50000.0,
            high=51000.0,
            low=49000.0,
            close=50500.0,
            volume=100.5,
        )
        insert_sync(db_url, [candle])

        # 2. Call the API — TestClient creates its own anyio event loop with fresh connections
        response = client.get(
            "/api/v1/ohlcv/BTC-USDT",
            params={
                "start_time": "2024-01-01T00:00:00Z",
                "end_time": "2024-01-02T00:00:00Z",
                "interval": "1m",
            },
        )

        # 3. Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["symbol"] == "BTC-USDT"
        assert data[0]["open"] == 50000.0
        assert data[0]["close"] == 50500.0
        assert data[0]["volume"] == 100.5

    finally:
        app.dependency_overrides.clear()
        asyncio.run(engine.dispose())


def test_volume_ranking_integration(postgres_container: PostgresContainer) -> None:
    """
    End-to-End integration test for the volume ranking endpoint.
    Verifies that TimescaleDB aggregates and ranks by total volume correctly.
    """
    db_url = postgres_container.get_connection_url()
    client, engine = make_test_client(db_url)

    try:
        now = datetime(2024, 6, 1, 12, 0, tzinfo=UTC)
        rows = [
            OHLCVModel(
                symbol="BTC-USDT", timestamp=now, open=1, high=1, low=1, close=1, volume=500.0
            ),
            OHLCVModel(
                symbol="ETH-USDT", timestamp=now, open=1, high=1, low=1, close=1, volume=1000.0
            ),
            OHLCVModel(
                symbol="ADA-USDT", timestamp=now, open=1, high=1, low=1, close=1, volume=250.0
            ),
        ]
        insert_sync(db_url, rows)

        response = client.get(
            "/api/v1/ranking/volume",
            params={
                "start_time": "2024-06-01T00:00:00Z",
                "end_time": "2024-06-02T00:00:00Z",
                "limit": 10,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

        # Verify descending order by volume
        assert data[0]["symbol"] == "ETH-USDT"
        assert data[0]["total_volume"] == 1000.0
        assert data[1]["symbol"] == "BTC-USDT"
        assert data[1]["total_volume"] == 500.0
        assert data[2]["symbol"] == "ADA-USDT"
        assert data[2]["total_volume"] == 250.0

    finally:
        app.dependency_overrides.clear()
        asyncio.run(engine.dispose())
