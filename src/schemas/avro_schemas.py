import io
from typing import Any, cast

from fastavro import parse_schema, schemaless_reader, schemaless_writer
from src.schemas.market_event import BaseMarketEvent

MARKET_EVENT_AVRO_SCHEMA: dict[str, Any] = {
    "type": "record",
    "name": "MarketEvent",
    "namespace": "com.market.events",
    "doc": "Avro schema for real-time market events",
    "fields": [
        {"name": "event_id", "type": "string"},
        {"name": "asset_class", "type": "string"},
        {"name": "symbol", "type": "string"},
        {"name": "price", "type": "double"},
        {"name": "volume", "type": "double"},
        {"name": "timestamp", "type": "double"},
        {"name": "source", "type": "string"},
    ],
}

PARSED_MARKET_EVENT_SCHEMA = parse_schema(MARKET_EVENT_AVRO_SCHEMA)


def serialize_avro(event: BaseMarketEvent) -> bytes:
    """Serialize a BaseMarketEvent Pydantic model to Avro binary format."""
    buffer = io.BytesIO()
    record = event.model_dump()
    # Enum field to string
    record["asset_class"] = str(record["asset_class"])
    schemaless_writer(buffer, PARSED_MARKET_EVENT_SCHEMA, record)
    return buffer.getvalue()


def deserialize_avro(payload: bytes) -> dict[str, Any]:
    """Deserialize Avro binary bytes back into a python dictionary."""
    buffer = io.BytesIO(payload)
    record = cast(dict[str, Any], schemaless_reader(buffer, PARSED_MARKET_EVENT_SCHEMA))
    return record
