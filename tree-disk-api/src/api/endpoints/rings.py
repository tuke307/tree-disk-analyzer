from fastapi import APIRouter, Response, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import treediskrings
from PIL import Image
import io
from io import BytesIO
import logging
import base64
import numpy as np
import cv2

from ...config.settings import OUTPUT_DIR, INPUT_DIR, DEBUG, SAVE_RESULTS

router = APIRouter()
logger = logging.getLogger(__name__)


def numpy_to_base64(img_array: np.ndarray) -> str:
    """Convert a numpy array to base64 string."""
    success, encoded_img = cv2.imencode(".png", img_array)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to encode image")
    return base64.b64encode(encoded_img.tobytes()).decode("utf-8")


@router.post(
    "/detect",
    responses={
        429: {"description": "Too Many Requests"},
    },
)
async def detect_rings(
    cx: int,
    cy: int,
    image: UploadFile = File(...),
) -> Response:
    """
    Detect the rings in the image.<br>
    """
    logger.debug("Rings detection endpoint called.")

    # Read and process image
    contents = await image.read()
    img = Image.open(io.BytesIO(contents))

    # save the image temporarily, to call the function
    path = f"{INPUT_DIR}/input_rings.png"
    img.save(path)

    treediskrings.configure(
        input_image=path,
        output_dir=OUTPUT_DIR,
        cx=cx,
        cy=cy,
        save_results=SAVE_RESULTS,
        debug=DEBUG,
    )

    result = treediskrings.run()

    if len(result) != 2:
        raise HTTPException(
            status_code=500, detail="Unexpected response format from tree disk analysis"
        )

    devernay_curves_p, img_out = result

    # Convert the image to base64
    img_base64 = numpy_to_base64(img_out)

    # Return the image as a response
    return JSONResponse(
        content={"devernay_curves_p": devernay_curves_p, "base64": img_base64}
    )
