from pydantic import BaseModel, Field


class OHLCV(BaseModel):
    """
    Schema for Windowed Aggregations (Open, High, Low, Close, Volume).
    Represents the aggregated metrics for a specific asset over a specific time window.
    """

    symbol: str = Field(..., description="The normalized symbol of the asset.")
    timestamp: float = Field(
        ..., description="UNIX timestamp indicating the start of the tumbling window."
    )
    open: float = Field(..., description="Opening price in the window.")
    high: float = Field(..., description="Highest price in the window.")
    low: float = Field(..., description="Lowest price in the window.")
    close: float = Field(..., description="Closing (or latest) price in the window.")
    volume: float = Field(default=0.0, description="Total volume traded in the window.")

    @classmethod
    def create_initial(cls, symbol: str, timestamp: float, price: float, volume: float) -> "OHLCV":
        """
        Helper method to create a new OHLCV instance from the first event in a window.
        """
        return cls(
            symbol=symbol,
            timestamp=timestamp,
            open=price,
            high=price,
            low=price,
            close=price,
            volume=volume,
        )

    def update(self, price: float, volume: float) -> None:
        """
        Helper method to update the OHLCV metrics with a new incoming price and volume.
        Updates high, low, close, and accumulates volume.
        """
        if price > self.high:
            self.high = price
        if price < self.low:
            self.low = price
        self.close = price
        self.volume += volume
