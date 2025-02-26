import pytest
from fastapi.testclient import TestClient
from pathlib import Path
from src.main import app

client = TestClient(app)

# Set root folder
root_folder = Path(__file__).parent.parent.absolute()


@pytest.mark.parametrize(
    "image_path, expected_response",
    [
        ("input/tree-disk4-seg.jpg", {"x": 1607, "y": 1245}),
    ],
)
def test_pith_endpoint(image_path, expected_response):
    input_image = root_folder / image_path

    with open(input_image, "rb") as image_file:
        response = client.post("/pith/detect", files={"image": image_file})

    assert response.status_code == 200
    response_json = response.json()
    assert abs(response_json["x"] - expected_response["x"]) <= 10
    assert abs(response_json["y"] - expected_response["y"]) <= 10
