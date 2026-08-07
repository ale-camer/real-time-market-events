from datetime import timedelta

from src.consumers.app import app
from src.schemas.ohlcv import OHLCV

# Define Faust Tables for stateful windowed aggregations.
# Tumbling windows create non-overlapping contiguous time blocks.
# We set `expires` to clear old window data from memory/RocksDB after a certain time.
crypto_ohlcv_1m = app.Table("crypto_ohlcv_1m").tumbling(60.0, expires=timedelta(hours=1))
stocks_ohlcv_1m = app.Table("stocks_ohlcv_1m").tumbling(60.0, expires=timedelta(hours=1))
forex_ohlcv_1m = app.Table("forex_ohlcv_1m").tumbling(60.0, expires=timedelta(hours=1))

# Define the outgoing topics where the closed window data can be forwarded.
# We use `# type: ignore[arg-type]` here as we did in topics.py to bypass mypy's strictness
# regarding Pydantic models vs faust.Record.
crypto_ohlcv_topic = app.topic("market.crypto.ohlcv.1m", value_type=OHLCV)  # type: ignore[arg-type]
stocks_ohlcv_topic = app.topic("market.stocks.ohlcv.1m", value_type=OHLCV)  # type: ignore[arg-type]
forex_ohlcv_topic = app.topic("market.forex.ohlcv.1m", value_type=OHLCV)  # type: ignore[arg-type]
