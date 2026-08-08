import logging
from datetime import UTC, datetime
from typing import Any

import faust
from src.consumers.app import app
from src.consumers.topics import crypto_topic, forex_topic, price_alerts_topic, stocks_topic
from src.schemas.alerts import PriceAnomalyAlert
from src.transformers.enrichment import enrich_event

logger = logging.getLogger(__name__)

# Faust Table to store the last known price for each symbol
# It persists data across worker restarts if a changelog topic is configured.
last_price_table = app.Table("last_price", default=float)

THRESHOLD_PERCENTAGE = 2.0


async def check_anomaly(symbol: str, current_price: float, timestamp: float) -> None:
    """Checks for price anomalies and emits an alert if detected."""
    previous_price = last_price_table[symbol]

    if previous_price > 0.0:
        change = ((current_price - previous_price) / previous_price) * 100

        if abs(change) >= THRESHOLD_PERCENTAGE:
            alert_type = "PUMP" if change > 0 else "DUMP"
            alert = PriceAnomalyAlert(
                symbol=symbol,
                timestamp=datetime.fromtimestamp(timestamp, tz=UTC)
                if isinstance(timestamp, float)
                else timestamp,
                previous_price=previous_price,
                current_price=current_price,
                percentage_change=change,
                alert_type=alert_type,  # type: ignore[arg-type]
            )
            logger.warning(f"🚨 ANOMALY: {symbol} {alert_type} by {change:.2f}%")
            await price_alerts_topic.send(value=alert)

    # Update the last price
    last_price_table[symbol] = current_price


@app.agent(crypto_topic)
async def detect_crypto_anomalies(stream: faust.StreamT[Any]) -> None:
    """Agent to detect anomalies in crypto events."""
    async for event in stream:
        try:
            enriched = enrich_event(event)
            await check_anomaly(
                enriched.normalized_symbol, event.price, enriched.processed_timestamp
            )
        except Exception as e:
            logger.error(f"Error in anomaly detection for crypto: {e}")


@app.agent(stocks_topic)
async def detect_stocks_anomalies(stream: faust.StreamT[Any]) -> None:
    """Agent to detect anomalies in stock events."""
    async for event in stream:
        try:
            enriched = enrich_event(event)
            await check_anomaly(
                enriched.normalized_symbol, event.price, enriched.processed_timestamp
            )
        except Exception as e:
            logger.error(f"Error in anomaly detection for stocks: {e}")


@app.agent(forex_topic)
async def detect_forex_anomalies(stream: faust.StreamT[Any]) -> None:
    """Agent to detect anomalies in forex events."""
    async for event in stream:
        try:
            enriched = enrich_event(event)
            await check_anomaly(
                enriched.normalized_symbol, event.price, enriched.processed_timestamp
            )
        except Exception as e:
            logger.error(f"Error in anomaly detection for forex: {e}")
