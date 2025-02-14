import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


@pytest.mark.parametrize(
    "path, expected_status, expected_response",
    [("/health", 200, {"status": "healthy"})],
)
def test_health(path, expected_status, expected_response):
    response = client.get(path)

    assert response.status_code == expected_status
    assert response.json() == expected_response
