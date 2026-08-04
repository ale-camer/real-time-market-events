import json
import logging
from collections.abc import Generator
from typing import cast
from unittest.mock import MagicMock, patch

import pytest
from confluent_kafka import KafkaError
from src.producers.kafka_producer import EventProducer


@pytest.fixture
def mock_producer_class() -> Generator[MagicMock, None, None]:
    with patch("src.producers.kafka_producer.Producer") as mock:
        yield mock


def test_producer_initialization(mock_producer_class: MagicMock) -> None:
    """Test that EventProducer initializes confluent_kafka.Producer with expected config."""
    producer = EventProducer(producer_config={"bootstrap.servers": "test:9092"})
    assert producer is not None
    mock_producer_class.assert_called_once()
    called_config = mock_producer_class.call_args[0][0]
    assert called_config["bootstrap.servers"] == "test:9092"
    assert called_config["acks"] == "all"


def test_produce_success(mock_producer_class: MagicMock) -> None:
    """Test that produce() serializes key and value to bytes and calls underlying producer."""
    mock_instance = mock_producer_class.return_value
    producer = EventProducer()

    topic = "market.events.crypto"
    key = "BTC-USD"
    value = {"symbol": "BTC", "price": 50000.0, "timestamp": 1690000000}

    producer.produce(topic=topic, key=key, value=value)

    mock_instance.produce.assert_called_once()
    call_kwargs = mock_instance.produce.call_args[1]

    assert call_kwargs["topic"] == topic
    assert call_kwargs["key"] == b"BTC-USD"
    assert json.loads(call_kwargs["value"].decode("utf-8")) == value
    mock_instance.poll.assert_called_once_with(0)


def test_delivery_report_success(
    mock_producer_class: MagicMock, caplog: pytest.LogCaptureFixture
) -> None:
    """Test that _delivery_report logs success when error is None."""
    caplog.set_level(logging.INFO)
    producer = EventProducer()

    mock_msg = MagicMock()
    mock_msg.topic.return_value = "test.topic"
    mock_msg.partition.return_value = 0
    mock_msg.offset.return_value = 42

    producer._delivery_report(err=None, msg=mock_msg)

    assert "Message delivered to topic 'test.topic' [0] at offset 42" in caplog.text


def test_delivery_report_error(
    mock_producer_class: MagicMock, caplog: pytest.LogCaptureFixture
) -> None:
    """Test that _delivery_report logs error when err is provided."""
    caplog.set_level(logging.ERROR)
    producer = EventProducer()

    mock_err = cast(KafkaError, Exception("Broker: Leader not available"))

    mock_msg = MagicMock()
    mock_msg.key.return_value = b"test_key"

    producer._delivery_report(err=mock_err, msg=mock_msg)

    assert "Message delivery failed for key" in caplog.text
    assert "Leader not available" in caplog.text


def test_produce_raises_exception_on_error(mock_producer_class: MagicMock) -> None:
    """Test that produce() raises and logs exceptions if serialization or produce fails."""
    mock_instance = mock_producer_class.return_value
    mock_instance.produce.side_effect = RuntimeError("Kafka buffer full")

    producer = EventProducer()

    with pytest.raises(RuntimeError, match="Kafka buffer full"):
        producer.produce("topic", "key", {"data": "test"})


def test_flush(mock_producer_class: MagicMock) -> None:
    """Test that flush() calls underlying producer's flush()."""
    mock_instance = mock_producer_class.return_value
    mock_instance.flush.return_value = 0

    producer = EventProducer()
    result = producer.flush(timeout=2.5)

    mock_instance.flush.assert_called_once_with(2.5)
    assert result == 0
