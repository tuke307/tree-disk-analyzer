import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_create_item():
    input_image = ("input/tree-disk4.png",)
    cx = (1204,)
    cy = (1264,)
    save_results = (True,)
    response = client.post("/items/", json={"name": "test item", "price": 10.5})
    assert response.status_code == 200
    assert response.json() == {
        "name": "test item",
        "price": 10.5,
    }  # Replace with your expected response


# Add more test functions as needed
