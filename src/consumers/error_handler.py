import traceback

from src.consumers.topics import dlq_topic
from src.schemas.dlq_event import DLQEvent


async def send_to_dlq(
    payload: dict[str, object] | str, error: Exception, source_topic: str
) -> None:
    """
    Constructs a DLQEvent from the failed payload and exception, and routes it
    to the dead-letter queue (DLQ) topic.

    Args:
        payload: The raw data that failed to process.
        error: The exception that was caught during processing.
        source_topic: The name of the Kafka topic the event originated from.
    """
    # Extract the stack trace as a string for debugging purposes
    tb_str = "".join(traceback.format_exception(type(error), error, error.__traceback__))

    # Construct the DLQ event
    dlq_event = DLQEvent(
        original_payload=payload,
        error_message=str(error),
        stack_trace=tb_str,
        source_topic=source_topic,
    )

    # Send the event to the dead-letter queue
    await dlq_topic.send(value=dlq_event)
