from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from src.db.repositories import get_ohlcv_history, get_top_volume_assets


@pytest.mark.asyncio
async def test_get_ohlcv_history_1m() -> None:
    session = AsyncMock()

    class MockCandle:
        def __init__(self) -> None:
            self.symbol = "BTC-USDT"
            self.timestamp = datetime(2023, 1, 1)
            self.open = 100.0
            self.high = 110.0
            self.low = 90.0
            self.close = 105.0
            self.volume = 50.0

    mock_result = MagicMock()
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = [MockCandle()]
    mock_result.scalars.return_value = mock_scalars
    session.execute.return_value = mock_result

    start_time = datetime(2023, 1, 1)
    end_time = datetime(2023, 1, 2)

    with patch("src.db.repositories.select") as mock_select:
        mock_where = mock_select.return_value.where.return_value
        mock_order_by = mock_where.order_by.return_value

        result = await get_ohlcv_history(session, "BTC-USDT", start_time, end_time, "1m")

        assert len(result) == 1
        assert result[0]["symbol"] == "BTC-USDT"
        assert result[0]["open"] == 100.0

        mock_select.assert_called_once()
        session.execute.assert_called_once_with(mock_order_by)


@pytest.mark.asyncio
async def test_get_ohlcv_history_time_bucket() -> None:
    session = AsyncMock()

    class MockBucketRow:
        def __init__(self) -> None:
            self.bucket = datetime(2023, 1, 1)
            self.open = 100.0
            self.high = 110.0
            self.low = 90.0
            self.close = 105.0
            self.volume = 50.0

    mock_result = MagicMock()
    mock_result.all.return_value = [MockBucketRow()]
    session.execute.return_value = mock_result

    start_time = datetime(2023, 1, 1)
    end_time = datetime(2023, 1, 2)

    with patch("src.db.repositories.select") as mock_select:
        mock_where = mock_select.return_value.where.return_value
        mock_group_by = mock_where.group_by.return_value
        mock_order_by = mock_group_by.order_by.return_value

        result = await get_ohlcv_history(session, "BTC-USDT", start_time, end_time, "1h")

        assert len(result) == 1
        assert result[0]["symbol"] == "BTC-USDT"
        assert result[0]["timestamp"] == datetime(2023, 1, 1)

        session.execute.assert_called_once_with(mock_order_by)


@pytest.mark.asyncio
async def test_get_top_volume_assets() -> None:
    session = AsyncMock()

    # Create a mock row class mimicking SQLAlchemy row proxy behavior
    class MockRow:
        def __init__(self, symbol: str, volume: float) -> None:
            self.symbol = symbol
            self.total_volume = volume

    mock_result = MagicMock()
    mock_result.all.return_value = [
        MockRow("BTC-USDT", 100.5),
        MockRow("ETH-USDT", 50.0),
    ]
    session.execute.return_value = mock_result

    start_time = datetime(2023, 1, 1)
    end_time = datetime(2023, 1, 2)

    with patch("src.db.repositories.select") as mock_select:
        mock_where = mock_select.return_value.where.return_value
        mock_group_by = mock_where.group_by.return_value
        mock_order_by = mock_group_by.order_by.return_value
        mock_limit = mock_order_by.limit.return_value

        result = await get_top_volume_assets(session, start_time, end_time, 5)

        assert len(result) == 2
        assert result[0]["symbol"] == "BTC-USDT"
        assert result[0]["total_volume"] == 100.5
        assert result[1]["symbol"] == "ETH-USDT"
        assert result[1]["total_volume"] == 50.0

        session.execute.assert_called_once_with(mock_limit)
