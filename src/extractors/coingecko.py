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


class CoinGeckoSettings(BaseSettings):
    coingecko_ws_url: str = "wss://ws.coingecko.com/crypto/price"
    coingecko_api_key: str | None = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class CoinGeckoExtractor:
    def __init__(self, pairs: list[str]) -> None:
        self.pairs = pairs
        self.settings = CoinGeckoSettings()
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

    async def _connect_and_read(self) -> None:
        """Connect to WebSocket and process messages."""
        logger.info(f"Connecting to {self.settings.coingecko_ws_url}...")

        async with websockets.connect(self.settings.coingecko_ws_url) as ws:
            logger.info("Connected. Sending subscription...")
            self.reconnect_delay = 1.0  # Reset delay on successful connection

            # Subscribe to the provided pairs
            sub_payload = {"action": "subscribe", "channel": "tickers", "pairs": self.pairs}
            if self.settings.coingecko_api_key:
                sub_payload["api_key"] = self.settings.coingecko_api_key

            await ws.send(json.dumps(sub_payload))
            logger.info(f"Subscribed to {self.pairs}")

            while not self._stop_event.is_set():
                # wait for message or cancellation
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

            if "event" in data and data["event"] == "ping":
                logger.debug("Received ping, ignoring.")
                return

            if "ticker" in data:
                normalized = self._normalize_ticker(data)
                logger.info(f"Market Event: {normalized}")
            else:
                logger.debug(f"Received non-ticker message: {data}")

        except json.JSONDecodeError:
            logger.warning(f"Received malformed JSON message: {raw_msg!r}")
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)

    def _normalize_ticker(self, data: dict[str, Any]) -> dict[str, Any]:
        """Normalize raw JSON into a standard dictionary."""
        ticker = data.get("ticker", {})
        return {
            "symbol": ticker.get("symbol", "UNKNOWN"),
            "price": float(ticker.get("price", 0.0)),
            "volume": float(ticker.get("volume", 0.0)),
            "timestamp": data.get("timestamp"),
        }

    def shutdown(self) -> None:
        """Trigger graceful shutdown."""
        logger.info("Shutdown signal received.")
        self._stop_event.set()
