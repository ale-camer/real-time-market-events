from typing import Any

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.models import MarketEventModel, OHLCVModel


async def bulk_insert_events(session: AsyncSession, events: list[dict[str, Any]]) -> None:
    """
    Inserts a batch of market events into the TimescaleDB hypertable.
    Uses on_conflict_do_nothing to silently ignore duplicate events.
    """
    if not events:
        return

    stmt = insert(MarketEventModel).values(events)
    # We ignore conflicts on unique constraints
    stmt = stmt.on_conflict_do_nothing()

    await session.execute(stmt)
    await session.commit()


async def bulk_insert_ohlcv(session: AsyncSession, candles: list[dict[str, Any]]) -> None:
    """
    Inserts or updates a batch of OHLCV candles in the TimescaleDB hypertable.
    Because tumbling windows can emit updates for the same minute interval,
    we use on_conflict_do_update based on the primary key (symbol, timestamp).
    """
    if not candles:
        return

    stmt = insert(OHLCVModel).values(candles)

    # If the candle already exists, update its values
    stmt = stmt.on_conflict_do_update(
        index_elements=["symbol", "timestamp"],
        set_={
            "open": stmt.excluded.open,
            "high": stmt.excluded.high,
            "low": stmt.excluded.low,
            "close": stmt.excluded.close,
            "volume": stmt.excluded.volume,
        },
    )

    await session.execute(stmt)
    await session.commit()
