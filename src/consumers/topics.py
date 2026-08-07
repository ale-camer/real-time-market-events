from src.consumers.app import app
from src.schemas.dlq_event import DLQEvent
from src.schemas.market_event import CryptoEvent, ForexEvent, StockEvent

# Define topics and link them to their respective Pydantic models
# This allows Faust to automatically deserialize the incoming JSON into these models.
crypto_topic = app.topic("market.crypto", value_type=CryptoEvent)  # type: ignore[arg-type]
stocks_topic = app.topic("market.stocks", value_type=StockEvent)  # type: ignore[arg-type]
forex_topic = app.topic("market.forex", value_type=ForexEvent)  # type: ignore[arg-type]
dlq_topic = app.topic("market.dlq", value_type=DLQEvent)  # type: ignore[arg-type]
