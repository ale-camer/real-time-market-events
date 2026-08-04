import time

import pytest
from pydantic import ValidationError
from src.schemas.avro_schemas import deserialize_avro, serialize_avro
from src.schemas.market_event import (
    AssetClass,
    CryptoEvent,
    ForexEvent,
    StockEvent,
)


def test_valid_crypto_event() -> None:
    """Test creating a valid CryptoEvent."""
    now = time.time()
    event = CryptoEvent(
        symbol="btc-usd",
        price=64000.50,
        volume=1.25,
        timestamp=now,
        source="coingecko",
    )

    assert event.asset_class == AssetClass.CRYPTO
    assert event.symbol == "BTC-USD"  # Symbol should be converted to uppercase
    assert event.price == 64000.50
    assert event.volume == 1.25
    assert event.timestamp == now
    assert event.source == "coingecko"
    assert event.event_id is not None


def test_valid_stock_event() -> None:
    """Test creating a valid StockEvent."""
    now = time.time()
    event = StockEvent(
        symbol="aapl",
        price=185.20,
        volume=1000.0,
        timestamp=now,
        source="polygon",
    )

    assert event.asset_class == AssetClass.STOCKS
    assert event.symbol == "AAPL"
    assert event.price == 185.20


def test_valid_forex_event() -> None:
    """Test creating a valid ForexEvent."""
    now = time.time()
    event = ForexEvent(
        symbol="eur/usd",
        price=1.0850,
        volume=0.0,  # Zero volume allowed
        timestamp=now,
        source="polygon",
    )

    assert event.asset_class == AssetClass.FOREX
    assert event.symbol == "EUR/USD"
    assert event.volume == 0.0


def test_invalid_price_zero_or_negative() -> None:
    """Test that zero or negative price raises a ValidationError."""
    now = time.time()
    with pytest.raises(ValidationError):
        CryptoEvent(
            symbol="BTC",
            price=0.0,
            volume=1.0,
            timestamp=now,
            source="coingecko",
        )

    with pytest.raises(ValidationError):
        CryptoEvent(
            symbol="BTC",
            price=-10.0,
            volume=1.0,
            timestamp=now,
            source="coingecko",
        )


def test_invalid_negative_volume() -> None:
    """Test that negative volume raises a ValidationError."""
    now = time.time()
    with pytest.raises(ValidationError):
        CryptoEvent(
            symbol="BTC",
            price=100.0,
            volume=-0.5,
            timestamp=now,
            source="coingecko",
        )


def test_invalid_empty_symbol() -> None:
    """Test that empty string symbol raises a ValidationError."""
    now = time.time()
    with pytest.raises(ValidationError):
        CryptoEvent(
            symbol="",
            price=100.0,
            volume=1.0,
            timestamp=now,
            source="coingecko",
        )


def test_avro_serialization_round_trip() -> None:
    """Test full round-trip: Pydantic model -> Avro binary bytes -> dict -> Pydantic model."""
    now = time.time()
    original_event = CryptoEvent(
        symbol="ETH-USD",
        price=3500.75,
        volume=10.5,
        timestamp=now,
        source="coingecko",
    )

    # Serialize to Avro binary
    avro_bytes = serialize_avro(original_event)
    assert isinstance(avro_bytes, bytes)
    assert len(avro_bytes) > 0

    # Deserialize back to dict
    deserialized_dict = deserialize_avro(avro_bytes)
    assert deserialized_dict["symbol"] == "ETH-USD"
    assert deserialized_dict["asset_class"] == "crypto"
    assert deserialized_dict["price"] == 3500.75
    assert deserialized_dict["volume"] == 10.5
    assert deserialized_dict["source"] == "coingecko"
    assert deserialized_dict["event_id"] == original_event.event_id

    # Re-instantiate Pydantic model from deserialized dict
    reconstructed_event = CryptoEvent(**deserialized_dict)
    assert reconstructed_event == original_event
