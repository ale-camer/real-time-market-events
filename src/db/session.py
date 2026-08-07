import os
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# For local development we fallback to the default localhost URL.
# In production or docker-compose, this will be overridden by the environment.
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/market_events",
)

# Instantiating the async engine that manages the connection pool
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set to True to debug SQL queries being generated
    pool_size=10,  # Maximum number of permanent connections
    max_overflow=20,  # Maximum number of extra connections during traffic spikes
)

# Creating the factory for generating new database sessions
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Asynchronous dependency generator for database sessions.
    It guarantees the session is closed when the context exits.
    Designed to be used natively with FastAPI's Depends() injection.
    """
    async with AsyncSessionLocal() as session:
        yield session
