from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
import treediskpith
from PIL import Image
import io
import logging

from ...config.settings import (
    OUTPUT_DIR,
    INPUT_DIR,
    YOLO_MODEL_PATH,
    DEBUG,
    SAVE_RESULTS,
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/detect",
    responses={
        429: {"description": "Too Many Requests"},
    },
)
async def detect_pith(
    image: UploadFile = File(...),
) -> JSONResponse:
    """
    Detect the pith in the image.<br>
    """
    logger.debug("Pith detection endpoint called.")

    # Read and process image
    contents = await image.read()
    img = Image.open(io.BytesIO(contents))

    # save the image temporarily, to call the function
    path = f"{INPUT_DIR}/input_pith.png"
    img.save(path)

    treediskpith.configure(
        input_image=path,
        model_path=YOLO_MODEL_PATH,
        output_dir=OUTPUT_DIR,
        save_results=SAVE_RESULTS,
        debug=DEBUG,
    )
    img_in, img_processed, pith = treediskpith.run()

    # Check if pith was detected
    if pith is None:
        raise HTTPException(status_code=404, detail="No pith detected in the image")

    data = {
        "x": int(pith[0]),
        "y": int(pith[1]),
    }

    # return pith tuple
    return JSONResponse(content=data)
