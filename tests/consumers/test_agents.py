import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.consumers.agents import process_crypto_events
from src.schemas.enriched_event import EnrichedMarketEvent
from src.schemas.market_event import CryptoEvent


@pytest.fixture
def crypto_event() -> CryptoEvent:
    return CryptoEvent(
        symbol="btcusdt",
        price=50000.0,
        volume=1.0,
        timestamp=1690891200.0,
        source="binance",
    )


@pytest.mark.asyncio
async def test_process_crypto_events_success(crypto_event: CryptoEvent) -> None:
    """
    Test the happy path of the crypto consumer agent.
    Verifies that incoming events are enriched and the tumbling
    window table is correctly updated.
    """
    enriched_event = EnrichedMarketEvent(
        **crypto_event.model_dump(),
        normalized_symbol="BTC-USDT",
    )

    with patch("src.consumers.agents.enrich_event", return_value=enriched_event) as mock_enrich, \
         patch("src.consumers.agents.crypto_ohlcv_1m") as mock_table:
        
        mock_window_wrapper = MagicMock()
        mock_window_wrapper.current.return_value = None  
        mock_table.__getitem__.return_value = mock_window_wrapper

        # Create a simple async generator to mock the Faust stream
        async def mock_stream():
            yield crypto_event

        # Bypass Faust's test_context to prevent event loop hanging
        await process_crypto_events.fun(mock_stream())
            
        mock_enrich.assert_called_once_with(crypto_event)
        mock_table.__getitem__.assert_called_once_with("BTC-USDT")
        mock_window_wrapper.current.assert_called_once()


@pytest.mark.asyncio
async def test_process_crypto_events_error_routes_to_dlq(crypto_event: CryptoEvent) -> None:
    """
    Test that if an exception is raised anywhere within the stream loop
    (e.g., parsing/enrichment failure), the agent catches it and routes
    the raw payload to the DLQ instead of crashing.
    """
    with patch("src.consumers.agents.enrich_event", side_effect=ValueError("Enrichment failed")), \
         patch("src.consumers.agents.send_to_dlq", new_callable=AsyncMock) as mock_dlq:

        async def mock_stream():
            yield crypto_event

        await process_crypto_events.fun(mock_stream())

        mock_dlq.assert_called_once()
        args, kwargs = mock_dlq.call_args
        assert args[0] == crypto_event.model_dump()
        assert isinstance(args[1], ValueError)
        assert args[2] == "market.crypto"
