import pytest
from fastapi.testclient import TestClient
from pathlib import Path
from src.main import app

client = TestClient(app)

# Set root folder
root_folder = Path(__file__).parent.parent.absolute()

@pytest.mark.parametrize("image_path, expected_response", [
    ("input/tree-disk4.png", {"x": 503, "y": 3355}),
])
def test_pith_endpoint(image_path, expected_response):
    input_image = root_folder / image_path

    with open(input_image, "rb") as image_file:
        response = client.post("/pith/detect", files={"image": image_file})
        
    assert response.status_code == 200
    assert response.json() == expected_response