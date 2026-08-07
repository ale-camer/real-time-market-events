from unittest.mock import AsyncMock, patch

import pytest
from src.consumers.error_handler import send_to_dlq
from src.schemas.dlq_event import DLQEvent


def test_dlq_event_instantiation() -> None:
    """
    Test that the DLQEvent schema can correctly handle different
    payload structures like dictionaries or raw strings.
    """
    # 1. Test with a dictionary payload
    dict_payload = {"symbol": "BTCUSD", "price": "invalid"}
    event_dict = DLQEvent(
        original_payload=dict_payload,
        error_message="ValueError: Could not convert string to float",
        source_topic="market.crypto",
    )
    assert event_dict.original_payload == dict_payload
    assert event_dict.error_message == "ValueError: Could not convert string to float"
    assert event_dict.source_topic == "market.crypto"
    assert event_dict.stack_trace is None
    assert event_dict.failed_at > 0

    # 2. Test with a string payload (e.g. malformed JSON)
    str_payload = "{this is completely broken json"
    event_str = DLQEvent(
        original_payload=str_payload,
        error_message="JSONDecodeError",
        source_topic="market.stocks",
        stack_trace="Traceback: line 1, column 2",
    )
    assert event_str.original_payload == str_payload
    assert event_str.stack_trace is not None


@pytest.mark.asyncio
async def test_send_to_dlq() -> None:
    """
    Test the asynchronous routing of failed events to the DLQ topic.
    Verifies that stack traces are captured and the Faust topic is called.
    """
    payload = {"symbol": "AAPL", "price": -50.0}

    # Force an exception to capture a real stack trace
    try:
        raise ValueError("Price cannot be negative")
    except ValueError as e:
        error = e

    source_topic = "market.stocks"

    # Patch the Faust topic where send_to_dlq attempts to send the message
    with patch("src.consumers.error_handler.dlq_topic") as mock_topic:
        # Faust topic.send is an async method
        mock_topic.send = AsyncMock()

        # Call the error handler
        await send_to_dlq(payload, error, source_topic)

        # Validate that the mock was called exactly once
        mock_topic.send.assert_called_once()

        # Extract the arguments passed to dlq_topic.send(value=...)
        call_kwargs = mock_topic.send.call_args.kwargs
        assert "value" in call_kwargs

        # Validate the DLQEvent that was constructed inside the function
        sent_event = call_kwargs["value"]
        assert isinstance(sent_event, DLQEvent)
        assert sent_event.original_payload == payload
        assert "Price cannot be negative" in sent_event.error_message
        assert sent_event.source_topic == source_topic
        # Ensure the traceback was correctly captured and stringified
        assert sent_event.stack_trace is not None
        assert "Traceback" in sent_event.stack_trace
        assert "raise ValueError" in sent_event.stack_trace
