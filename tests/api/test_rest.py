from collections.abc import AsyncGenerator
from datetime import datetime
from unittest.mock import AsyncMock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient
from src.api.routes.rest import router
from src.db.session import get_db_session

# Setup a lightweight test app injecting our router
app = FastAPI()
app.include_router(router)


# Dependency Override for the async database session
async def override_get_db_session() -> AsyncGenerator[AsyncMock, None]:
    yield AsyncMock()


app.dependency_overrides[get_db_session] = override_get_db_session

client = TestClient(app)


@patch("src.api.routes.rest.get_ohlcv_history")
def test_api_get_ohlcv_history(mock_get_history: AsyncMock) -> None:
    # Setup mock return value mimicking the DB repository
    mock_get_history.return_value = [
        {
            "symbol": "BTC-USDT",
            "timestamp": datetime(2023, 1, 1),
            "open": 100.0,
            "high": 110.0,
            "low": 90.0,
            "close": 105.0,
            "volume": 50.0,
        }
    ]

    response = client.get(
        "/api/v1/ohlcv/BTC-USDT",
        params={
            "start_time": "2023-01-01T00:00:00Z",
            "end_time": "2023-01-02T00:00:00Z",
            "interval": "1m",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["symbol"] == "BTC-USDT"
    # Pydantic/FastAPI automatically serializes datetime to ISO format
    assert data[0]["timestamp"] == "2023-01-01T00:00:00"


@patch("src.api.routes.rest.get_top_volume_assets")
def test_api_get_top_volume_ranking(mock_get_top_volume: AsyncMock) -> None:
    mock_get_top_volume.return_value = [{"symbol": "BTC-USDT", "total_volume": 1000.5}]

    response = client.get(
        "/api/v1/ranking/volume",
        params={
            "start_time": "2023-01-01T00:00:00Z",
            "end_time": "2023-01-02T00:00:00Z",
            "limit": 5,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["symbol"] == "BTC-USDT"
    assert data[0]["total_volume"] == 1000.5
