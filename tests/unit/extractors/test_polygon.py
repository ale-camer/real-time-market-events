import asyncio
import json
import logging
from unittest.mock import AsyncMock, patch

import pytest
from src.extractors.polygon import PolygonExtractor
from websockets.exceptions import ConnectionClosedError


@pytest.fixture
def extractor(monkeypatch: pytest.MonkeyPatch) -> PolygonExtractor:
    logging.getLogger("src.extractors.polygon").disabled = False
    # Use a small reconnect delay for tests to run fast
    # Also set a fake API key so it attempts auth
    monkeypatch.setenv("POLYGON_API_KEY", "fake_test_key")
    ext = PolygonExtractor(symbols=["T.AAPL"])
    ext.reconnect_delay = 0.01
    ext.max_reconnect_delay = 0.05
    return ext


@pytest.mark.asyncio
async def test_successful_auth_sub_and_message(
    extractor: PolygonExtractor, caplog: pytest.LogCaptureFixture
) -> None:
    """Test full flow: auth -> subscribe -> message parse -> log."""
    caplog.set_level(logging.INFO, logger="src.extractors.polygon")

    mock_ws = AsyncMock()

    # Create a sequence of messages for recv
    auth_response = json.dumps([{"ev": "status", "status": "auth_success", "message": "auth OK"}])
    market_message = json.dumps(
        [{"ev": "T", "sym": "AAPL", "p": 150.25, "s": 100, "t": 1690000000}]
    )

    recv_state = {"count": 0}

    async def mock_recv() -> str:
        count = recv_state["count"]
        recv_state["count"] += 1

        if count == 0:
            return auth_response
        elif count == 1:
            return market_message

        # Block forever after sending our messages
        await asyncio.sleep(10)
        return ""

    mock_ws.recv = mock_recv

    async def stop_later() -> None:
        await asyncio.sleep(0.05)
        extractor.shutdown()

    with patch("websockets.connect", return_value=AsyncMock()) as mock_connect:
        mock_connect.return_value.__aenter__.return_value = mock_ws
        await asyncio.gather(extractor.run(), stop_later())

    # Check sends
    assert mock_ws.send.call_count >= 2
    auth_payload = json.loads(mock_ws.send.call_args_list[0][0][0])
    sub_payload = json.loads(mock_ws.send.call_args_list[1][0][0])

    assert auth_payload["action"] == "auth"
    assert auth_payload["params"] == "fake_test_key"

    assert sub_payload["action"] == "subscribe"
    assert sub_payload["params"] == "T.AAPL"

    # Check that the message was parsed and logged
    log_text = caplog.text
    assert "Market Event" in log_text
    assert "'symbol': 'AAPL'" in log_text
    assert "'price': 150.25" in log_text


@pytest.mark.asyncio
async def test_auth_failure_no_api_key(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    """Test that it aborts connection loop if no API key is set."""
    caplog.set_level(logging.ERROR, logger="src.extractors.polygon")
    monkeypatch.delenv("POLYGON_API_KEY", raising=False)

    # We don't use the fixture because we changed the env var
    ext = PolygonExtractor(symbols=["T.AAPL"])

    mock_ws = AsyncMock()
    with patch("websockets.connect", return_value=AsyncMock()) as mock_connect:
        mock_connect.return_value.__aenter__.return_value = mock_ws

        async def stop_later() -> None:
            await asyncio.sleep(0.05)
            ext.shutdown()

        await asyncio.gather(ext.run(), stop_later())

    assert "No POLYGON_API_KEY provided. Cannot authenticate." in caplog.text
    # Should not have sent anything since it didn't auth
    mock_ws.send.assert_not_called()


@pytest.mark.asyncio
async def test_reconnect_on_connection_closed(
    extractor: PolygonExtractor, caplog: pytest.LogCaptureFixture
) -> None:
    """Test exponential backoff on ConnectionClosedError."""
    caplog.set_level(logging.WARNING, logger="src.extractors.polygon")

    error_mock = AsyncMock(side_effect=ConnectionClosedError(None, None))

    async def stop_later() -> None:
        await asyncio.sleep(0.1)
        extractor.shutdown()

    with patch.object(extractor, "_connect_and_read", new=error_mock):
        await asyncio.gather(extractor.run(), stop_later())

    assert "WebSocket connection closed" in caplog.text
    assert error_mock.call_count > 1


@pytest.mark.asyncio
async def test_shutdown_cleanly(extractor: PolygonExtractor) -> None:
    """Test that calling shutdown() cleanly stops the run loop."""
    mock_ws = AsyncMock()

    async def mock_recv() -> str:
        # Initial auth response, then block
        if not hasattr(mock_recv, "called"):
            mock_recv.called = True  # type: ignore
            return json.dumps([{"ev": "status", "status": "auth_success"}])
        await asyncio.sleep(10)
        return ""

    mock_ws.recv = mock_recv

    async def trigger_shutdown() -> None:
        await asyncio.sleep(0.02)
        extractor.shutdown()

    with patch("websockets.connect", return_value=AsyncMock()) as mock_connect:
        mock_connect.return_value.__aenter__.return_value = mock_ws

        await asyncio.wait_for(asyncio.gather(extractor.run(), trigger_shutdown()), timeout=1.0)

    mock_ws.close.assert_called_once()
