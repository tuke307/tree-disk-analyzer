from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
from typing import List
import treediskpithdetector
from PIL import Image
import io
from io import BytesIO

from ...config import OUTPUT_DIR, INPUT_DIR, YOLO_MODEL_PATH

router = APIRouter()


@router.post(
    "/detect",
    responses={
        429: {"description": "Too Many Requests"},
    },
)
async def segment_image(
    image: UploadFile = File(...),
) -> None:
    """
    Sample endpoint.<br>
    Example usage: http://127.0.0.1:8000/sample
    """
    # Read and process image
    contents = await image.read()
    img = Image.open(io.BytesIO(contents))

    # save the image temporarily, to call the function
    path = f"{INPUT_DIR}/input_pith.png"
    img.save(path)

    treediskpithdetector.configure(
        input_image=path,
        model_path=YOLO_MODEL_PATH,
        output_dir=OUTPUT_DIR,
        method="apd_dl",
        save_results=True,
        debug=True,
    )
    img_in, img_processed, pith = treediskpithdetector.run()

    data = {
        "x": int(pith[0]),
        "y": int(pith[1]),
    }

    # return pith tuple
    return JSONResponse(content=data)
