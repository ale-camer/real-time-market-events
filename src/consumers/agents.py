import logging

import faust
from src.consumers.aggregations import crypto_ohlcv_1m, forex_ohlcv_1m, stocks_ohlcv_1m
from src.consumers.app import app
from src.consumers.error_handler import send_to_dlq
from src.consumers.topics import crypto_topic, forex_topic, stocks_topic
from src.schemas.market_event import CryptoEvent, ForexEvent, StockEvent
from src.schemas.ohlcv import OHLCV
from src.transformers.enrichment import enrich_event

logger = logging.getLogger(__name__)


@app.agent(crypto_topic)
async def process_crypto_events(stream: faust.StreamT[CryptoEvent]) -> None:
    """Skeleton agent to consume and log crypto events."""
    async for event in stream:
        try:
            enriched_event = enrich_event(event)
            sym = enriched_event.normalized_symbol

            # Retrieve the current tumbling window value
            current_ohlcv = crypto_ohlcv_1m[sym].current()

            if not current_ohlcv:
                crypto_ohlcv_1m[sym] = OHLCV.create_initial(
                    symbol=sym,
                    timestamp=enriched_event.processed_timestamp,
                    price=event.price,
                    volume=event.volume,
                )
            else:
                current_ohlcv.update(event.price, event.volume)
                crypto_ohlcv_1m[sym] = current_ohlcv

            logger.info(f"Updated Crypto OHLCV for {sym}")
        except Exception as e:
            logger.error(f"Error processing crypto event, routing to DLQ: {e}")
            await send_to_dlq(event.model_dump(), e, "market.crypto")


@app.agent(stocks_topic)
async def process_stock_events(stream: faust.StreamT[StockEvent]) -> None:
    """Skeleton agent to consume and log stock events."""
    async for event in stream:
        try:
            enriched_event = enrich_event(event)
            sym = enriched_event.normalized_symbol

            current_ohlcv = stocks_ohlcv_1m[sym].current()

            if not current_ohlcv:
                stocks_ohlcv_1m[sym] = OHLCV.create_initial(
                    symbol=sym,
                    timestamp=enriched_event.processed_timestamp,
                    price=event.price,
                    volume=event.volume,
                )
            else:
                current_ohlcv.update(event.price, event.volume)
                stocks_ohlcv_1m[sym] = current_ohlcv

            logger.info(f"Updated Stock OHLCV for {sym}")
        except Exception as e:
            logger.error(f"Error processing stock event, routing to DLQ: {e}")
            await send_to_dlq(event.model_dump(), e, "market.stocks")


@app.agent(forex_topic)
async def process_forex_events(stream: faust.StreamT[ForexEvent]) -> None:
    """Skeleton agent to consume and log forex events."""
    async for event in stream:
        try:
            enriched_event = enrich_event(event)
            sym = enriched_event.normalized_symbol

            current_ohlcv = forex_ohlcv_1m[sym].current()

            if not current_ohlcv:
                forex_ohlcv_1m[sym] = OHLCV.create_initial(
                    symbol=sym,
                    timestamp=enriched_event.processed_timestamp,
                    price=event.price,
                    volume=event.volume,
                )
            else:
                current_ohlcv.update(event.price, event.volume)
                forex_ohlcv_1m[sym] = current_ohlcv

            logger.info(f"Updated Forex OHLCV for {sym}")
        except Exception as e:
            logger.error(f"Error processing forex event, routing to DLQ: {e}")
            await send_to_dlq(event.model_dump(), e, "market.forex")


# Import anomaly_agent so that Faust discovers the new anomaly detection agents
import src.consumers.anomaly_agent  # noqa: F401, E402
