import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_database_connection(db_session: AsyncSession) -> None:
    """
    Validates that the Testcontainers PostgreSQL instance is running
    and that SQLAlchemy can connect and execute queries against it.
    """
    # Execute a simple query
    result = await db_session.execute(text("SELECT 1"))
    value = result.scalar()

    assert value == 1


@pytest.mark.asyncio
async def test_database_tables_exist(db_session: AsyncSession) -> None:
    """
    Validates that Alembic migrations were successfully applied
    by checking for the existence of the expected tables.
    """
    # Check if market_events exists
    result_events = await db_session.execute(
        text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'market_events')")
    )
    assert result_events.scalar() is True

    # Check if ohlcv_candles exists
    result_ohlcv = await db_session.execute(
        text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'ohlcv_candles')")
    )
    assert result_ohlcv.scalar() is True
