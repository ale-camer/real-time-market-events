import os
from collections.abc import AsyncGenerator
from urllib.parse import urlparse, parse_qs, urlunparse

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

raw_url = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/market_events",
)

# Parse URL to clean up parameters incompatible with asyncpg
parsed = urlparse(raw_url)
# Clean path if query string leaked into path
clean_path = parsed.path.split("?")[0].split("&")[0]

connect_args = {"ssl": "require"}

# Construct asyncpg URL without query string arguments that asyncpg parses as database name
clean_url = urlunparse((
    "postgresql+asyncpg",
    parsed.netloc,
    clean_path,
    "",
    "",
    ""
))

pool_size = int(os.getenv("DB_POOL_SIZE", 2))
max_overflow = int(os.getenv("DB_MAX_OVERFLOW", 3))

# Instantiating the async engine that manages the connection pool
engine = create_async_engine(
    clean_url,
    echo=False,
    pool_size=pool_size,
    max_overflow=max_overflow,
    connect_args=connect_args,
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
