import json
import logging
from unittest.mock import MagicMock, patch

import pytest
from src.producers.kafka_producer import EventProducer


@pytest.fixture
def producer(monkeypatch: pytest.MonkeyPatch) -> EventProducer:
    monkeypatch.setenv("KAFKA_BOOTSTRAP_SERVERS", "fake-broker:9092")

    with patch("src.producers.kafka_producer.Producer") as mock_producer_class:
        mock_instance = MagicMock()
        mock_producer_class.return_value = mock_instance
        producer = EventProducer()
        # Attach the mock instance to the fixture so we can assert on it easily
        producer._mock_instance = mock_instance  # type: ignore[attr-defined]
        return producer


def test_producer_initialization(producer: EventProducer) -> None:
    """Test that the producer initializes with correct config."""
    assert producer.settings.kafka_bootstrap_servers == "fake-broker:9092"
    assert producer.producer is not None


def test_produce_success(producer: EventProducer, caplog: pytest.LogCaptureFixture) -> None:
    """Test producing a message successfully."""
    caplog.set_level(logging.INFO)

    topic = "market.crypto"
    key = "BTC-USD"
    value = {"symbol": "BTC-USD", "price": 50000.0, "volume": 1.5}

    producer.produce(topic=topic, key=key, value=value)

    # Assert that producer.produce was called with correct arguments
    mock_prod = producer._mock_instance  # type: ignore[attr-defined]
    mock_prod.produce.assert_called_once()

    call_args, call_kwargs = mock_prod.produce.call_args
    assert call_kwargs["topic"] == topic
    assert call_kwargs["key"] == b"BTC-USD"
    assert json.loads(call_kwargs["value"]) == value

    # Assert that poll was called
    mock_prod.poll.assert_called_once_with(0)


def test_produce_exception(producer: EventProducer, caplog: pytest.LogCaptureFixture) -> None:
    """Test handling of exceptions during produce."""
    caplog.set_level(logging.ERROR)

    mock_prod = producer._mock_instance  # type: ignore[attr-defined]
    mock_prod.produce.side_effect = Exception("Kafka connection down")

    with pytest.raises(Exception, match="Kafka connection down"):
        producer.produce(topic="market.crypto", key="BTC", value={"price": 100})

    assert "Failed to produce message to topic 'market.crypto' with key 'BTC'" in caplog.text


def test_flush(producer: EventProducer) -> None:
    """Test flush method calls underlying producer flush."""
    mock_prod = producer._mock_instance  # type: ignore[attr-defined]
    mock_prod.flush.return_value = 0

    remaining = producer.flush(timeout=1.0)

    mock_prod.flush.assert_called_once_with(1.0)
    assert remaining == 0


def test_delivery_report(producer: EventProducer, caplog: pytest.LogCaptureFixture) -> None:
    """Test the delivery report callback."""
    caplog.set_level(logging.INFO)

    mock_msg = MagicMock()
    mock_msg.topic.return_value = "market.crypto"
    mock_msg.partition.return_value = 0
    mock_msg.offset.return_value = 123
    mock_msg.key.return_value = b"BTC-USD"

    # Test successful delivery
    producer._delivery_report(err=None, msg=mock_msg)
    assert "Message delivered to topic 'market.crypto' [0] at offset 123" in caplog.text

    # Test failed delivery
    producer._delivery_report(err="NetworkError", msg=mock_msg)  # type: ignore[arg-type]
    assert "Message delivery failed for key 'b'BTC-USD'': NetworkError" in caplog.text
