import datetime
from collections import defaultdict
from collections.abc import Generator
from unittest.mock import AsyncMock, patch

import pytest
from src.consumers.anomaly_agent import THRESHOLD_PERCENTAGE, check_anomaly
from src.schemas.alerts import PriceAnomalyAlert


@pytest.fixture(autouse=True)
def mock_faust_table() -> Generator[defaultdict[str, float], None, None]:
    """Mock the Faust table as a simple dictionary to avoid stream iteration errors."""
    fake_table: defaultdict[str, float] = defaultdict(float)
    with patch("src.consumers.anomaly_agent.last_price_table", fake_table):
        yield fake_table


@pytest.mark.asyncio
@patch("src.consumers.anomaly_agent.price_alerts_topic.send", new_callable=AsyncMock)
async def test_anomaly_detected_pump(
    mock_send: AsyncMock, mock_faust_table: defaultdict[str, float]
) -> None:
    """Test that a price pump > THRESHOLD_PERCENTAGE triggers an alert."""
    symbol = "BTC/USD"
    ts1 = datetime.datetime.now(datetime.UTC).timestamp()
    ts2 = ts1 + 1.0

    # First event sets the baseline
    await check_anomaly(symbol, 100.0, ts1)

    # Assert no alert on the first event
    mock_send.assert_not_called()
    assert mock_faust_table[symbol] == 100.0

    # Second event is a 5% pump
    pump_price = 100.0 * (1 + (THRESHOLD_PERCENTAGE + 3.0) / 100)  # 5% pump
    await check_anomaly(symbol, pump_price, ts2)

    # Assert alert was sent
    mock_send.assert_called_once()

    # Validate the alert contents
    call_args = mock_send.call_args[1]
    alert: PriceAnomalyAlert = call_args["value"]
    assert alert.symbol == symbol
    assert alert.alert_type == "PUMP"
    assert alert.percentage_change >= THRESHOLD_PERCENTAGE
    assert alert.previous_price == 100.0
    assert alert.current_price == pump_price


@pytest.mark.asyncio
@patch("src.consumers.anomaly_agent.price_alerts_topic.send", new_callable=AsyncMock)
async def test_anomaly_detected_dump(
    mock_send: AsyncMock, mock_faust_table: defaultdict[str, float]
) -> None:
    """Test that a price dump > THRESHOLD_PERCENTAGE triggers an alert."""
    symbol = "ETH/USD"
    ts1 = datetime.datetime.now(datetime.UTC).timestamp()
    ts2 = ts1 + 1.0

    # First event sets the baseline
    await check_anomaly(symbol, 2000.0, ts1)
    mock_send.assert_not_called()

    # Second event is a 10% dump
    dump_price = 2000.0 * (1 - (THRESHOLD_PERCENTAGE + 8.0) / 100)  # 10% dump
    await check_anomaly(symbol, dump_price, ts2)

    # Assert alert was sent
    mock_send.assert_called_once()

    # Validate the alert contents
    call_args = mock_send.call_args[1]
    alert: PriceAnomalyAlert = call_args["value"]
    assert alert.symbol == symbol
    assert alert.alert_type == "DUMP"
    assert alert.percentage_change <= -THRESHOLD_PERCENTAGE


@pytest.mark.asyncio
@patch("src.consumers.anomaly_agent.price_alerts_topic.send", new_callable=AsyncMock)
async def test_no_anomaly_detected(
    mock_send: AsyncMock, mock_faust_table: defaultdict[str, float]
) -> None:
    """Test that normal price movements do not trigger alerts."""
    symbol = "EUR/USD"
    ts1 = datetime.datetime.now(datetime.UTC).timestamp()
    ts2 = ts1 + 1.0

    # Baseline
    await check_anomaly(symbol, 1.1000, ts1)

    # 0.5% change (below threshold)
    safe_price = 1.1000 * (1 + (THRESHOLD_PERCENTAGE - 1.5) / 100)
    await check_anomaly(symbol, safe_price, ts2)

    # Assert NO alert was sent
    mock_send.assert_not_called()
    assert mock_faust_table[symbol] == safe_price
