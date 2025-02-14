import pytest
from fastapi.testclient import TestClient
from pathlib import Path
from src.main import app

client = TestClient(app)

# Set root folder
root_folder = Path(__file__).parent.parent.absolute()


@pytest.mark.parametrize(
    "image_path, cx, cy",
    [
        ("input/tree-disk4.png", 1204, 1264),
    ],
)
def test_rings_endpoint(image_path, cx, cy):
    input_image = root_folder / image_path

    with open(input_image, "rb") as image_file:
        response = client.post(
            f"/rings/detect?cx={cx}&cy={cy}", files={"image": image_file}
        )

    assert response.status_code == 200
    assert response.headers["Content-Type"].startswith("image/")
