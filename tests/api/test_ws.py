from unittest.mock import AsyncMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.api.routes.ws import manager, router

# Setup a lightweight test app injecting our router
app = FastAPI()
app.include_router(router)

# Note: We must use the regular TestClient (not AsyncClient) for WebSockets
client = TestClient(app)


def test_websocket_market_endpoint() -> None:
    # TestClient allows using `websocket_connect` as a synchronous context manager
    with client.websocket_connect("/ws/market/BTC-USDT") as websocket:
        # Verify the manager correctly registered the connection
        assert "BTC-USDT" in manager.active_connections
        assert len(manager.active_connections["BTC-USDT"]) == 1
        
        # Test bidirectional communication (ping/pong keepalive)
        websocket.send_text("ping")
        data = websocket.receive_text()
        assert data == "pong"
    
    # Upon exiting the context block, the WebSocket disconnects automatically.
    # We assert that the manager cleaned up the state.
    assert "BTC-USDT" not in manager.active_connections


@pytest.mark.asyncio
async def test_connection_manager_broadcast() -> None:
    """
    Test the ConnectionManager's broadcast logic directly using an AsyncMock.
    """
    mock_ws = AsyncMock()
    
    # Simulate a connection
    await manager.connect(mock_ws, "ETH-USDT")
    assert "ETH-USDT" in manager.active_connections
    
    # Broadcast a mock JSON message
    message = {"symbol": "ETH-USDT", "price": 2000.0}
    await manager.broadcast_to_symbol(message, "ETH-USDT")
    
    # Verify the manager called send_json on the websocket
    mock_ws.send_json.assert_called_once_with(message)
    
    # Simulate a disconnection
    manager.disconnect(mock_ws, "ETH-USDT")
    assert "ETH-USDT" not in manager.active_connections
