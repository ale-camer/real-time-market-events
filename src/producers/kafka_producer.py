import json
import logging
from typing import Any

from confluent_kafka import KafkaError, Message, Producer
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


class KafkaProducerSettings(BaseSettings):
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_security_protocol: str = "PLAINTEXT"
    kafka_sasl_mechanism: str | None = None
    kafka_sasl_username: str | None = None
    kafka_sasl_password: str | None = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class EventProducer:
    def __init__(self, producer_config: dict[str, Any] | None = None) -> None:
        self.settings = KafkaProducerSettings()

        config = {
            "bootstrap.servers": self.settings.kafka_bootstrap_servers,
            "security.protocol": self.settings.kafka_security_protocol,
            "acks": "all",
            "retries": 3,
            "retry.backoff.ms": 100,
        }

        if self.settings.kafka_sasl_mechanism:
            config["sasl.mechanism"] = self.settings.kafka_sasl_mechanism
        if self.settings.kafka_sasl_username:
            config["sasl.username"] = self.settings.kafka_sasl_username
        if self.settings.kafka_sasl_password:
            config["sasl.password"] = self.settings.kafka_sasl_password

        # Override defaults if custom config provided
        if producer_config:
            config.update(producer_config)

        logger.info(f"Initializing Kafka Producer connected to: {config.get('bootstrap.servers')}")
        self.producer = Producer(config)

    def _delivery_report(self, err: KafkaError | None, msg: Message) -> None:
        """Callback executed once message is delivered or fails."""
        if err is not None:
            logger.error(f"Message delivery failed for key '{msg.key()!r}': {err}")
        else:
            logger.info(
                f"Message delivered to topic '{msg.topic()}' "
                f"[{msg.partition()}] at offset {msg.offset()}"
            )

    def produce(self, topic: str, key: str, value: dict[str, Any]) -> None:
        """Serialize payload to JSON and produce to specified Kafka topic."""
        try:
            serialized_value = json.dumps(value).encode("utf-8")
            serialized_key = key.encode("utf-8")

            self.producer.produce(
                topic=topic,
                key=serialized_key,
                value=serialized_value,
                on_delivery=self._delivery_report,
            )
            # Poll events to trigger callbacks
            self.producer.poll(0)

        except Exception as e:
            logger.error(
                f"Failed to produce message to topic '{topic}' with key '{key}': {e}",
                exc_info=True,
            )
            raise

    def flush(self, timeout: float = 5.0) -> int:
        """Flush outstanding messages from queue."""
        logger.info("Flushing pending Kafka messages...")
        return self.producer.flush(timeout)
