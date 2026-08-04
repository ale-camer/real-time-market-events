import asyncio
import json
import logging
from typing import Any

import websockets
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


class PolygonSettings(BaseSettings):
    polygon_ws_url: str = "wss://delayed.polygon.io/stocks"
    polygon_api_key: str | None = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class PolygonExtractor:
    def __init__(self, symbols: list[str]) -> None:
        self.symbols = symbols
        self.settings = PolygonSettings()
        self._stop_event = asyncio.Event()
        self.reconnect_delay = 1.0
        self.max_reconnect_delay = 60.0

    async def run(self) -> None:
        """Main loop with automatic reconnection."""
        while not self._stop_event.is_set():
            try:
                await self._connect_and_read()
            except websockets.ConnectionClosed as e:
                logger.warning(
                    f"WebSocket connection closed: {e}. Reconnecting in {self.reconnect_delay}s..."
                )
                await asyncio.sleep(self.reconnect_delay)
                self.reconnect_delay = min(self.reconnect_delay * 2, self.max_reconnect_delay)
            except Exception as e:
                logger.error(
                    f"Unexpected error in WebSocket connection: {e}. "
                    f"Reconnecting in {self.reconnect_delay}s..."
                )
                await asyncio.sleep(self.reconnect_delay)
                self.reconnect_delay = min(self.reconnect_delay * 2, self.max_reconnect_delay)
            else:
                if not self._stop_event.is_set():
                    await asyncio.sleep(self.reconnect_delay)

    async def _connect_and_read(self) -> None:
        """Connect to WebSocket, authenticate, subscribe and process messages."""
        logger.info(f"Connecting to {self.settings.polygon_ws_url}...")

        async with websockets.connect(self.settings.polygon_ws_url) as ws:
            logger.info("Connected. Sending authentication...")

            # Authenticate
            if not self.settings.polygon_api_key:
                logger.error("No POLYGON_API_KEY provided. Cannot authenticate.")
                return

            auth_payload = {"action": "auth", "params": self.settings.polygon_api_key}
            await ws.send(json.dumps(auth_payload))

            # Wait for auth confirmation
            auth_response = await ws.recv()
            logger.info(f"Auth response: {auth_response!r}")

            self.reconnect_delay = 1.0  # Reset delay on successful connection

            # Subscribe to the provided symbols
            # Polygon subscription format for trades is usually 'T.SYMBOL'
            symbols_str = ",".join(self.symbols)
            sub_payload = {"action": "subscribe", "params": symbols_str}
            await ws.send(json.dumps(sub_payload))
            logger.info(f"Subscribed to {self.symbols}")

            while not self._stop_event.is_set():
                message_task = asyncio.create_task(ws.recv())
                stop_task = asyncio.create_task(self._stop_event.wait())

                done, pending = await asyncio.wait(
                    [message_task, stop_task], return_when=asyncio.FIRST_COMPLETED
                )

                if stop_task in done:
                    message_task.cancel()
                    logger.info("Shutdown requested. Closing WebSocket...")
                    await ws.close()
                    break

                if message_task in done:
                    msg = message_task.result()
                    self._process_message(msg)

    def _process_message(self, raw_msg: str | bytes) -> None:
        """Parse and normalize incoming WebSocket messages."""
        try:
            data = json.loads(raw_msg)

            # Polygon sends an array of events
            if isinstance(data, list):
                for event in data:
                    ev_type = event.get("ev")
                    if ev_type == "status":
                        logger.debug(f"Status event: {event}")
                    elif ev_type in ("T", "Q", "A", "AM"):
                        normalized = self._normalize_event(event)
                        logger.info(f"Market Event: {normalized}")
                    else:
                        logger.debug(f"Received unknown event type: {event}")
            else:
                logger.debug(f"Received non-list message: {data}")

        except json.JSONDecodeError:
            logger.warning(f"Received malformed JSON message: {raw_msg!r}")
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)

    def _normalize_event(self, event: dict[str, Any]) -> dict[str, Any]:
        """Normalize raw JSON into a standard dictionary."""
        return {
            "symbol": event.get("sym", "UNKNOWN"),
            # p for trades, c for aggregates
            "price": float(event.get("p", event.get("c", 0.0))),
            # s for trade size, v for aggregate volume
            "volume": float(event.get("s", event.get("v", 0.0))),
            "timestamp": event.get("t"),
            "original_event_type": event.get("ev"),
        }

    def shutdown(self) -> None:
        """Trigger graceful shutdown."""
        logger.info("Shutdown signal received.")
        self._stop_event.set()
