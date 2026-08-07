from src.db.models import Base, MarketEventModel, OHLCVModel


def test_models_in_metadata() -> None:
    """Verifies that both models are correctly registered in the SQLAlchemy Base."""
    tables = Base.metadata.tables.keys()
    assert "market_events" in tables
    assert "ohlcv_candles" in tables


def test_market_event_columns() -> None:
    """Verifies that the MarketEventModel has all the expected columns."""
    columns = MarketEventModel.__table__.columns.keys()
    expected_columns = ["id", "timestamp", "symbol", "asset_class", "price", "volume"]
    
    for col in expected_columns:
        assert col in columns


def test_ohlcv_columns() -> None:
    """Verifies that the OHLCVModel has all the expected columns."""
    columns = OHLCVModel.__table__.columns.keys()
    expected_columns = ["symbol", "timestamp", "open", "high", "low", "close", "volume"]
    
    for col in expected_columns:
        assert col in columns
