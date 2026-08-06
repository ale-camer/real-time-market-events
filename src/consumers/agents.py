import logging

import faust
from src.consumers.app import app
from src.consumers.topics import crypto_topic, forex_topic, stocks_topic
from src.schemas.market_event import CryptoEvent, ForexEvent, StockEvent

logger = logging.getLogger(__name__)


@app.agent(crypto_topic)
async def process_crypto_events(stream: faust.StreamT[CryptoEvent]) -> None:
    """Skeleton agent to consume and log crypto events."""
    async for event in stream:
        logger.info(f"Received Crypto event: {event}")


@app.agent(stocks_topic)
async def process_stock_events(stream: faust.StreamT[StockEvent]) -> None:
    """Skeleton agent to consume and log stock events."""
    async for event in stream:
        logger.info(f"Received Stock event: {event}")


@app.agent(forex_topic)
async def process_forex_events(stream: faust.StreamT[ForexEvent]) -> None:
    """Skeleton agent to consume and log forex events."""
    async for event in stream:
        logger.info(f"Received Forex event: {event}")
