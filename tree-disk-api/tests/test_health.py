import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

@pytest.mark.parametrize("expected_status, expected_response", [
    ("/", 200, {"status": "healthy"})
])
def test_health(expected_status, expected_response):
    response = client.get("/health")

    assert response.status_code == expected_status
    assert response.json() == expected_response