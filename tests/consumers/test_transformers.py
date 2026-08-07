from src.schemas.enriched_event import EnrichedMarketEvent
from src.schemas.market_event import AssetClass, CryptoEvent
from src.transformers.enrichment import enrich_event
from src.transformers.normalization import normalize_symbol, normalize_timestamp


def test_normalize_symbol_crypto() -> None:
    # It should separate known quote currencies
    assert normalize_symbol("btcusdt", "crypto") == "BTC-USDT"
    assert normalize_symbol("ETHUSD", "crypto") == "ETH-USD"

    # It should not modify already separated or unknown patterns
    assert normalize_symbol("SOL-EUR", "crypto") == "SOL-EUR"
    assert normalize_symbol("DOGECOIN", "crypto") == "DOGECOIN"


def test_normalize_symbol_forex() -> None:
    # Forex is strictly 6 characters usually
    assert normalize_symbol("eurusd", "forex") == "EUR-USD"
    assert normalize_symbol("GBPJPY", "forex") == "GBP-JPY"

    # If already formatted, it shouldn't break
    assert normalize_symbol("USD-CAD", "forex") == "USD-CAD"


def test_normalize_symbol_stocks() -> None:
    # Stocks just get uppercased
    assert normalize_symbol("aapl", "stocks") == "AAPL"
    assert normalize_symbol("MSFT", "stocks") == "MSFT"


def test_normalize_timestamp() -> None:
    # 2023-08-01 12:00:00 UTC
    ts = 1690891200.0
    result = normalize_timestamp(ts)
    # Checks that +00:00 is replaced with Z and milliseconds are present
    assert result == "2023-08-01T12:00:00.000Z"


def test_enrich_event_crypto() -> None:
    # Given a raw event
    raw_event = CryptoEvent(
        symbol="btcusdt", price=50000.0, volume=1.5, timestamp=1690891200.0, source="binance"
    )

    # When enriched
    enriched = enrich_event(raw_event)

    # Then it returns the proper EnrichedMarketEvent with normalized fields
    assert isinstance(enriched, EnrichedMarketEvent)
    assert enriched.normalized_symbol == "BTC-USDT"
    assert enriched.asset_class == AssetClass.CRYPTO
    assert enriched.price == 50000.0
    assert enriched.volume == 1.5

    # And processed metadata is auto-injected
    assert enriched.processed_timestamp > 0.0

    # And base identifiers are preserved
    assert enriched.event_id == raw_event.event_id
    assert enriched.source == raw_event.source
