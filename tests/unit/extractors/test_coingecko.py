import asyncio
import json
import logging
from unittest.mock import AsyncMock, patch

import pytest
from src.extractors.coingecko import CoinGeckoExtractor
from websockets.exceptions import ConnectionClosedError


@pytest.fixture
def extractor() -> CoinGeckoExtractor:
    # Use a small reconnect delay for tests to run fast
    ext = CoinGeckoExtractor(pairs=["bitcoin"])
    ext.reconnect_delay = 0.01
    ext.max_reconnect_delay = 0.05
    return ext


@pytest.mark.asyncio
async def test_successful_connection_and_message(
    extractor: CoinGeckoExtractor, caplog: pytest.LogCaptureFixture
) -> None:
    """Test that a valid ticker message is correctly parsed and logged."""
    caplog.set_level(logging.INFO)

    valid_message = json.dumps(
        {
            "ticker": {
                "symbol": "BTC-USD",
                "price": "60000.50",
                "volume": "1200.5",
            },
            "timestamp": 1690000000,
        }
    )

    mock_ws = AsyncMock()

    state = {"called": False}

    # Mock recv to yield one message and then block until shutdown
    async def mock_recv() -> str:
        if not state["called"]:
            state["called"] = True
            return valid_message

        # Block until cancelled or shutdown
        await asyncio.sleep(10)
        return ""

    mock_ws.recv = mock_recv

    # We need to simulate the extractor stopping after a short time
    async def stop_later() -> None:
        await asyncio.sleep(0.05)
        extractor.shutdown()

    with patch("websockets.connect", return_value=AsyncMock()) as mock_connect:
        mock_connect.return_value.__aenter__.return_value = mock_ws

        await asyncio.gather(extractor.run(), stop_later())

    # Check that subscription was sent
    mock_ws.send.assert_called_once()
    sent_payload = json.loads(mock_ws.send.call_args[0][0])
    assert sent_payload["action"] == "subscribe"
    assert sent_payload["pairs"] == ["bitcoin"]

    # Check that the message was parsed and logged
    log_text = caplog.text
    assert "Market Event" in log_text
    assert "'symbol': 'BTC-USD'" in log_text
    assert "'price': 60000.5" in log_text


@pytest.mark.asyncio
async def test_unexpected_format_does_not_crash(
    extractor: CoinGeckoExtractor, caplog: pytest.LogCaptureFixture
) -> None:
    """Test that a malformed JSON message is handled gracefully."""
    caplog.set_level(logging.WARNING)

    mock_ws = AsyncMock()

    state = {"called": False}

    async def mock_recv() -> str:
        if not state["called"]:
            state["called"] = True
            return "invalid json payload{"
        await asyncio.sleep(10)
        return ""

    mock_ws.recv = mock_recv

    async def stop_later() -> None:
        await asyncio.sleep(0.05)
        extractor.shutdown()

    with patch("websockets.connect", return_value=AsyncMock()) as mock_connect:
        mock_connect.return_value.__aenter__.return_value = mock_ws
        await asyncio.gather(extractor.run(), stop_later())

    assert "Received malformed JSON message" in caplog.text


@pytest.mark.asyncio
async def test_reconnect_on_connection_closed(
    extractor: CoinGeckoExtractor, caplog: pytest.LogCaptureFixture
) -> None:
    """Test exponential backoff on ConnectionClosed."""
    caplog.set_level(logging.WARNING)

    # This will cause _connect_and_read to raise ConnectionClosedError immediately
    error_mock = AsyncMock(side_effect=ConnectionClosedError(None, None))

    # We run the extractor and let it fail a few times, then stop
    async def stop_later() -> None:
        await asyncio.sleep(0.1)
        extractor.shutdown()

    with patch.object(extractor, "_connect_and_read", new=error_mock):
        await asyncio.gather(extractor.run(), stop_later())

    assert "WebSocket connection closed" in caplog.text
    # Ensure it tried to connect multiple times due to retry loop
    assert error_mock.call_count > 1


@pytest.mark.asyncio
async def test_shutdown_cleanly(extractor: CoinGeckoExtractor) -> None:
    """Test that calling shutdown() cleanly stops the run loop."""
    mock_ws = AsyncMock()

    async def mock_recv() -> str:
        await asyncio.sleep(10)
        return ""

    mock_ws.recv = mock_recv

    async def trigger_shutdown() -> None:
        # Give it a tiny moment to start
        await asyncio.sleep(0.02)
        extractor.shutdown()

    with patch("websockets.connect", return_value=AsyncMock()) as mock_connect:
        mock_connect.return_value.__aenter__.return_value = mock_ws

        # This will hang forever if shutdown doesn't work
        await asyncio.wait_for(asyncio.gather(extractor.run(), trigger_shutdown()), timeout=1.0)

    # Assert websocket was closed
    mock_ws.close.assert_called_once()
