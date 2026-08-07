from datetime import datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.models import OHLCVModel


async def get_ohlcv_history(
    session: AsyncSession,
    symbol: str,
    start_time: datetime,
    end_time: datetime,
    interval: str = "1m",
) -> list[dict[str, Any]]:
    """
    Fetches the OHLCV history for a given symbol within a specific time range.
    If interval is > '1m', it utilizes TimescaleDB's time_bucket to dynamically
    aggregate 1-minute candles into larger windows.
    """
    if interval == "1m":
        stmt = (
            select(OHLCVModel)
            .where(
                OHLCVModel.symbol == symbol,
                OHLCVModel.timestamp >= start_time,
                OHLCVModel.timestamp <= end_time,
            )
            .order_by(OHLCVModel.timestamp.asc())
        )
        result = await session.execute(stmt)
        return [
            {
                "symbol": row.symbol,
                "timestamp": row.timestamp,
                "open": row.open,
                "high": row.high,
                "low": row.low,
                "close": row.close,
                "volume": row.volume,
            }
            for row in result.scalars().all()
        ]

    # Map API friendly intervals to PostgreSQL interval syntax
    interval_map = {
        "5m": "5 minutes",
        "15m": "15 minutes",
        "1h": "1 hour",
        "4h": "4 hours",
        "1d": "1 day",
    }
    pg_interval = interval_map.get(interval, "1 hour")

    bucket = func.time_bucket(pg_interval, OHLCVModel.timestamp).label("bucket")

    stmt = (
        select(
            bucket,
            func.first(OHLCVModel.open, OHLCVModel.timestamp).label("open"),
            func.max(OHLCVModel.high).label("high"),
            func.min(OHLCVModel.low).label("low"),
            func.last(OHLCVModel.close, OHLCVModel.timestamp).label("close"),
            func.sum(OHLCVModel.volume).label("volume"),
        )
        .where(
            OHLCVModel.symbol == symbol,
            OHLCVModel.timestamp >= start_time,
            OHLCVModel.timestamp <= end_time,
        )
        .group_by(bucket)
        .order_by(bucket.asc())
    )
    result = await session.execute(stmt)

    return [
        {
            "symbol": symbol,
            "timestamp": row.bucket,
            "open": row.open,
            "high": row.high,
            "low": row.low,
            "close": row.close,
            "volume": row.volume,
        }
        for row in result.all()
    ]


async def get_top_volume_assets(
    session: AsyncSession,
    start_time: datetime,
    end_time: datetime,
    limit: int = 10,
) -> list[dict[str, Any]]:
    """
    Calculates and returns the top assets by total traded volume within a specific time range.
    Uses SQLAlchemy's func.sum to aggregate over the OHLCV hypertable.
    """
    stmt = (
        select(
            OHLCVModel.symbol,
            func.sum(OHLCVModel.volume).label("total_volume"),
        )
        .where(
            OHLCVModel.timestamp >= start_time,
            OHLCVModel.timestamp <= end_time,
        )
        .group_by(OHLCVModel.symbol)
        .order_by(func.sum(OHLCVModel.volume).desc())
        .limit(limit)
    )
    result = await session.execute(stmt)

    # Extract the rows into dictionaries for easy API serialization
    return [{"symbol": row.symbol, "total_volume": row.total_volume} for row in result.all()]
