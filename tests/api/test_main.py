from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


def test_health_check() -> None:
    """
    Verifies that the FastAPI application initializes correctly
    and the root health check endpoint returns a 200 OK status.
    """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_routers_included() -> None:
    """
    Verifies that the REST routers were successfully mounted onto the main FastAPI
    application by checking the generated OpenAPI schema.
    """
    # In newer FastAPI versions, app.routes uses _IncludedRouter lazy loading.
    # The safest way to verify registered REST endpoints is via the OpenAPI JSON.
    response = client.get("/openapi.json")
    assert response.status_code == 200

    schema = response.json()
    paths = schema.get("paths", {})

    # Assert REST endpoints are documented and available
    assert "/api/v1/ranking/volume" in paths
    assert "/api/v1/ohlcv/{symbol}" in paths
