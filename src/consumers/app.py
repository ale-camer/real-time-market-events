import logging
import os

import faust

# Configure basic logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

KAFKA_BROKER_URL = os.getenv("KAFKA_BROKER_URL", "kafka://localhost:9092")

logger.info(f"Initializing Faust app with broker: {KAFKA_BROKER_URL}")

app = faust.App(
    "market-events-processor",
    broker=KAFKA_BROKER_URL,
    value_serializer="json",  # Default serializer for the app
)
