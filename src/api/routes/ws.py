import logging
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ws", tags=["WebSockets"])


class ConnectionManager:
    """
    Manages active WebSocket connections to allow broadcasting
    real-time Kafka events directly to connected frontend clients.
    """
    def __init__(self) -> None:
        # Maps a market symbol to a list of active websocket connections
        self.active_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, symbol: str) -> None:
        await websocket.accept()
        if symbol not in self.active_connections:
            self.active_connections[symbol] = []
        self.active_connections[symbol].append(websocket)
        logger.info(f"Client connected to stream: {symbol}")

    def disconnect(self, websocket: WebSocket, symbol: str) -> None:
        if symbol in self.active_connections:
            if websocket in self.active_connections[symbol]:
                self.active_connections[symbol].remove(websocket)
            # Cleanup empty lists
            if not self.active_connections[symbol]:
                del self.active_connections[symbol]
        logger.info(f"Client disconnected from stream: {symbol}")

    async def broadcast_to_symbol(self, message: dict[str, Any], symbol: str) -> None:
        """
        Pushes a real-time JSON message (e.g. a new candlestick or price tick)
        to all clients currently subscribed to this specific symbol.
        """
        if symbol in self.active_connections:
            for connection in self.active_connections[symbol]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Failed to send message to client on {symbol}: {e}")


# Singleton instance to be shared across the FastAPI app
manager = ConnectionManager()


@router.websocket("/market/{symbol}")
async def websocket_market_endpoint(websocket: WebSocket, symbol: str) -> None:
    """
    WebSocket endpoint for frontend clients to subscribe to real-time market data.
    """
    await manager.connect(websocket, symbol)
    try:
        while True:
            # We keep the connection open and listen for any client messages.
            # Usually clients just listen, but they can send a 'ping' to keep the connection alive.
            data = await websocket.receive_text()
            if data.lower() == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(websocket, symbol)
