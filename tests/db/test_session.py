import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import engine, get_db_session


def test_engine_initialization() -> None:
    """
    Verifies that the SQLAlchemy async engine is correctly initialized
    using the postgresql+asyncpg driver.
    """
    assert engine.name == "postgresql"
    assert engine.driver == "asyncpg"


@pytest.mark.asyncio
async def test_get_db_session_yields_session() -> None:
    """
    Verifies that the session dependency generator correctly yields
    an instance of AsyncSession without actually connecting to the DB.
    """
    # Instantiate the async generator
    generator = get_db_session()
    
    # Fetch the first yielded value
    session = await anext(generator)
    
    # Verify the type
    assert isinstance(session, AsyncSession)
    
    # Close the generator cleanly to avoid ResourceWarnings
    await generator.aclose()
