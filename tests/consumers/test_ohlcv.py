from src.schemas.ohlcv import OHLCV


def test_ohlcv_create_initial() -> None:
    """
    Tests that a new OHLCV object is correctly initialized
    from the first price and volume in a time window.
    """
    symbol = "BTC-USDT"
    timestamp = 1690891200.0
    price = 50000.0
    volume = 1.5

    ohlcv = OHLCV.create_initial(
        symbol=symbol,
        timestamp=timestamp,
        price=price,
        volume=volume,
    )

    assert ohlcv.symbol == symbol
    assert ohlcv.timestamp == timestamp
    # All price bounds should equal the initial price
    assert ohlcv.open == price
    assert ohlcv.high == price
    assert ohlcv.low == price
    assert ohlcv.close == price

    assert ohlcv.volume == volume


def test_ohlcv_update_logic() -> None:
    """
    Tests the OHLCV mathematical aggregation logic.
    Ensures high/low bounds expand, close always updates, and volume accumulates.
    """
    # 1. Initialize
    ohlcv = OHLCV.create_initial(
        symbol="BTC-USDT",
        timestamp=1690891200.0,
        price=50000.0,
        volume=1.0,
    )

    # 2. Update with a HIGHER price
    ohlcv.update(price=51000.0, volume=0.5)
    assert ohlcv.open == 50000.0  # Open must never change
    assert ohlcv.high == 51000.0  # High should increase
    assert ohlcv.low == 50000.0  # Low remains the same
    assert ohlcv.close == 51000.0  # Close updates to latest
    assert ohlcv.volume == 1.5  # Volume accumulates (1.0 + 0.5)

    # 3. Update with a LOWER price
    ohlcv.update(price=49000.0, volume=2.0)
    assert ohlcv.open == 50000.0
    assert ohlcv.high == 51000.0  # High remains the same
    assert ohlcv.low == 49000.0  # Low should decrease
    assert ohlcv.close == 49000.0  # Close updates to latest
    assert ohlcv.volume == 3.5  # Volume accumulates (1.5 + 2.0)

    # 4. Update with an IN-BETWEEN price
    ohlcv.update(price=50500.0, volume=1.0)
    assert ohlcv.open == 50000.0
    assert ohlcv.high == 51000.0  # High remains the same
    assert ohlcv.low == 49000.0  # Low remains the same
    assert ohlcv.close == 50500.0  # Close updates to latest
    assert ohlcv.volume == 4.5  # Volume accumulates (3.5 + 1.0)
