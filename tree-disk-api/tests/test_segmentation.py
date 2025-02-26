import pytest
from fastapi.testclient import TestClient
from pathlib import Path
from src.main import app

client = TestClient(app)

# Set root folder
root_folder = Path(__file__).parent.parent.absolute()


@pytest.mark.parametrize(
    "image_path",
    [
        ("input/tree-disk4.jpg"),
    ],
)
def test_segmentation_endpoint(image_path):
    input_image = root_folder / image_path

    with open(input_image, "rb") as image_file:
        response = client.post(f"/segmentation/image", files={"image": image_file})

    assert response.status_code == 200
    assert response.headers["Content-Type"].startswith("image/")
