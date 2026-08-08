from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class PriceAnomalyAlert(BaseModel):
    """
    Schema for price anomaly alerts.
    Represents an unusual price movement (pump or dump).
    """

    symbol: str = Field(..., description="Trading pair symbol, e.g. BTC/USD")
    timestamp: datetime = Field(..., description="Timestamp of the event that triggered the alert")
    previous_price: float = Field(..., description="The last recorded price before the anomaly")
    current_price: float = Field(..., description="The current price that triggered the anomaly")
    percentage_change: float = Field(..., description="Change from previous to current price")
    alert_type: Literal["PUMP", "DUMP"] = Field(..., description="Type of the anomaly")
