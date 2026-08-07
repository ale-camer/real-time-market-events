from unittest.mock import AsyncMock, patch

import pytest
from src.loaders.db_writer import bulk_insert_events, bulk_insert_ohlcv


@pytest.mark.asyncio
async def test_bulk_insert_events_empty_list() -> None:
    session = AsyncMock()
    await bulk_insert_events(session, [])
    session.execute.assert_not_called()
    session.commit.assert_not_called()


@pytest.mark.asyncio
async def test_bulk_insert_events() -> None:
    session = AsyncMock()
    events = [
        {"symbol": "BTC-USDT", "price": 50000.0, "volume": 1.0, "timestamp": "2023-01-01T00:00:00Z"}
    ]

    with patch("src.loaders.db_writer.insert") as mock_insert:
        mock_stmt = mock_insert.return_value.values.return_value.on_conflict_do_nothing.return_value
        await bulk_insert_events(session, events)

        mock_insert.assert_called_once()
        session.execute.assert_called_once_with(mock_stmt)
        session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_bulk_insert_ohlcv() -> None:
    session = AsyncMock()
    candles = [
        {
            "symbol": "BTC-USDT",
            "timestamp": "2023-01-01T00:00:00Z",
            "open": 1,
            "high": 2,
            "low": 1,
            "close": 2,
            "volume": 100,
        }
    ]

    with patch("src.loaders.db_writer.insert") as mock_insert:
        mock_stmt = mock_insert.return_value.values.return_value.on_conflict_do_update.return_value
        await bulk_insert_ohlcv(session, candles)

        mock_insert.assert_called_once()
        session.execute.assert_called_once_with(mock_stmt)
        session.commit.assert_called_once()
