from collections.abc import AsyncGenerator
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
from src.loaders.agent import load_crypto_events, load_crypto_ohlcv


@pytest.mark.asyncio
async def test_load_crypto_events_batch() -> None:
    events_batch = [{"symbol": "BTC-USDT", "price": 50000.0}]

    # Mock stream and its take() method
    mock_stream = AsyncMock()

    async def mock_take(*args: Any, **kwargs: Any) -> AsyncGenerator[list[dict[str, Any]], None]:  # noqa: ANN401
        yield events_batch

    mock_stream.take = mock_take

    with (
        patch("src.loaders.agent.get_db_session") as mock_get_session,
        patch("src.loaders.agent.bulk_insert_events") as mock_bulk_insert,
    ):
        mock_generator = AsyncMock()
        mock_session = AsyncMock()

        # Setup the dependency injection mock
        mock_generator.__anext__.return_value = mock_session
        mock_get_session.return_value = mock_generator

        # Call the underlying function to bypass Faust test_context hanging
        await load_crypto_events.fun(mock_stream)  # type: ignore[misc]

        mock_bulk_insert.assert_called_once_with(mock_session, events_batch)
        mock_generator.aclose.assert_called_once()


@pytest.mark.asyncio
async def test_load_crypto_ohlcv_batch() -> None:
    candles_batch = [{"symbol": "BTC-USDT", "close": 50000.0}]

    mock_stream = AsyncMock()

    async def mock_take(*args: Any, **kwargs: Any) -> AsyncGenerator[list[dict[str, Any]], None]:  # noqa: ANN401
        yield candles_batch

    mock_stream.take = mock_take

    with (
        patch("src.loaders.agent.get_db_session") as mock_get_session,
        patch("src.loaders.agent.bulk_insert_ohlcv") as mock_bulk_insert,
    ):
        mock_generator = AsyncMock()
        mock_session = AsyncMock()

        mock_generator.__anext__.return_value = mock_session
        mock_get_session.return_value = mock_generator

        await load_crypto_ohlcv.fun(mock_stream)  # type: ignore[misc]

        mock_bulk_insert.assert_called_once_with(mock_session, candles_batch)
        mock_generator.aclose.assert_called_once()
