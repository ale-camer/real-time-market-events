import logging
from typing import Any

import faust
from src.db.session import get_db_session
from src.loaders.db_writer import bulk_insert_events, bulk_insert_ohlcv

logger = logging.getLogger(__name__)

# We create a distinct Faust app for the Loader.
# This allows us to scale the loader independently from the stream processor.
loader_app = faust.App(
    "timescaledb-loader",
    broker="kafka://localhost:9092",
    value_serializer="json",
)

crypto_enriched_topic = loader_app.topic("market.crypto.enriched")
crypto_ohlcv_topic = loader_app.topic("market.crypto.ohlcv.1m")


@loader_app.agent(crypto_enriched_topic)
async def load_crypto_events(stream: faust.StreamT[Any]) -> None:
    """
    Consumes enriched crypto events, buffers them, and inserts them in bulk.
    """
    # stream.take() buffers events up to max_ items or within seconds
    async for events_batch in stream.take(500, within=5.0):
        if not events_batch:
            continue

        try:
            # Instantiate an async DB session
            generator = get_db_session()
            session = await anext(generator)

            await bulk_insert_events(session, events_batch)
            logger.info(f"Bulk inserted {len(events_batch)} crypto events.")

            await generator.aclose()
        except Exception as e:
            logger.error(f"Error bulk inserting crypto events: {e}")
            raise


@loader_app.agent(crypto_ohlcv_topic)
async def load_crypto_ohlcv(stream: faust.StreamT[Any]) -> None:
    """
    Consumes OHLCV candles, buffers them, and inserts/updates them in bulk.
    """
    async for candles_batch in stream.take(500, within=5.0):
        if not candles_batch:
            continue

        try:
            generator = get_db_session()
            session = await anext(generator)

            await bulk_insert_ohlcv(session, candles_batch)
            logger.info(f"Bulk inserted/updated {len(candles_batch)} OHLCV candles.")

            await generator.aclose()
        except Exception as e:
            logger.error(f"Error bulk inserting OHLCV candles: {e}")
            raise
