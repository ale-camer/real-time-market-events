from enum import StrEnum
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator


class AssetClass(StrEnum):
    CRYPTO = "crypto"
    STOCKS = "stocks"
    FOREX = "forex"


class BaseMarketEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid4()))
    asset_class: AssetClass
    symbol: str = Field(..., min_length=1)
    price: float = Field(..., gt=0.0)
    volume: float = Field(..., ge=0.0)
    timestamp: float = Field(..., gt=0.0)
    source: str = Field(..., min_length=1)

    @field_validator("symbol")
    @classmethod
    def symbol_must_be_uppercase(cls, v: str) -> str:
        return v.strip().upper()


class CryptoEvent(BaseMarketEvent):
    asset_class: AssetClass = AssetClass.CRYPTO


class StockEvent(BaseMarketEvent):
    asset_class: AssetClass = AssetClass.STOCKS


class ForexEvent(BaseMarketEvent):
    asset_class: AssetClass = AssetClass.FOREX
