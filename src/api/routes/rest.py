from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.repositories import get_ohlcv_history, get_top_volume_assets
from src.db.session import get_db_session

router = APIRouter(prefix="/api/v1", tags=["REST API"])


@router.get("/ohlcv/{symbol}", response_model=list[dict[str, Any]])
async def api_get_ohlcv_history(
    symbol: str,
    start_time: datetime,
    end_time: datetime,
    interval: str = "1m",
    session: AsyncSession = Depends(get_db_session),  # noqa: B008
) -> list[dict[str, Any]]:
    """
    Returns the OHLCV candlestick history for a given symbol within a specified timeframe.
    Intervals greater than '1m' are dynamically aggregated using TimescaleDB's time_bucket.
    """
    return await get_ohlcv_history(session, symbol, start_time, end_time, interval)


@router.get("/ranking/volume", response_model=list[dict[str, Any]])
async def api_get_top_volume_ranking(
    start_time: datetime,
    end_time: datetime,
    limit: int = 10,
    session: AsyncSession = Depends(get_db_session),  # noqa: B008
) -> list[dict[str, Any]]:
    """
    Returns the top 'limit' assets sorted by total traded volume within a specific timeframe.
    Uses native SQLAlchemy summation functions over the hypertable.
    """
    return await get_top_volume_assets(session, start_time, end_time, limit)
