from time import time

from pydantic import Field
from src.schemas.market_event import BaseMarketEvent


class EnrichedMarketEvent(BaseMarketEvent):
    """
    Extends the base market event with transformed and enriched fields
    ready for downstream consumption (e.g., aggregation or TimescaleDB).
    """

    processed_timestamp: float = Field(
        default_factory=time,
        description="UNIX timestamp of when the event was processed by Faust.",
    )
    normalized_symbol: str = Field(
        ...,
        min_length=1,
        description="Standardized symbol format (e.g., BTC/USD or AAPL).",
    )
