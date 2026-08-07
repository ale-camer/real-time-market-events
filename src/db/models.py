from datetime import datetime

from sqlalchemy import DateTime, Float, Index, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for SQLAlchemy declarative models."""

    pass


class MarketEventModel(Base):
    """
    Model representing raw/enriched market events.
    In TimescaleDB, if a table is a hypertable partitioned by time,
    the time column must be part of any primary key.
    Thus, we use a composite primary key (id, timestamp).
    """

    __tablename__ = "market_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), primary_key=True, nullable=False
    )

    symbol: Mapped[str] = mapped_column(String(50), nullable=False)
    asset_class: Mapped[str] = mapped_column(String(50), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    volume: Mapped[float] = mapped_column(Float, nullable=False)

    # Added an index for faster querying by symbol + time
    __table_args__ = (Index("ix_market_events_symbol_time", "symbol", "timestamp"),)


class OHLCVModel(Base):
    """
    Model representing 1-minute windowed OHLCV candles.
    The primary key is naturally composite: (symbol, timestamp).
    """

    __tablename__ = "ohlcv_candles"

    symbol: Mapped[str] = mapped_column(String(50), primary_key=True, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), primary_key=True, nullable=False
    )

    open: Mapped[float] = mapped_column(Float, nullable=False)
    high: Mapped[float] = mapped_column(Float, nullable=False)
    low: Mapped[float] = mapped_column(Float, nullable=False)
    close: Mapped[float] = mapped_column(Float, nullable=False)
    volume: Mapped[float] = mapped_column(Float, nullable=False)

    __table_args__ = (Index("ix_ohlcv_candles_symbol_time", "symbol", "timestamp"),)
