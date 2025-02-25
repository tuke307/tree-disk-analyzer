from fastapi import APIRouter, Response, UploadFile, File
import treedisksegmentation
from PIL import Image
import io
from io import BytesIO
import logging
import cv2

from ...config.settings import (
    OUTPUT_DIR,
    INPUT_DIR,
    YOLO_SEG_MODEL_PATH,
    DEBUG,
    SAVE_RESULTS,
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/image",
    responses={
        429: {"description": "Too Many Requests"},
    },
)
async def segment_image(
    image: UploadFile = File(...),
) -> Response:
    """
    Segment the image and return the segmented image.<br>
    """
    logger.debug("Segmentation endpoint called.")

    # Read and process image
    contents = await image.read()
    img = Image.open(io.BytesIO(contents))

    # save the image temporarily, to call the function
    path = f"{INPUT_DIR}/input_segmentation.png"
    img.save(path)

    treedisksegmentation.configure(
        input_image=path,
        model_path=YOLO_SEG_MODEL_PATH,
        output_dir=OUTPUT_DIR,
        save_results=SAVE_RESULTS,
        debug=DEBUG,
    )
    result_image, masks = treedisksegmentation.run()

    # Convert color space from RGB to BGR
    result_image_rgb = cv2.cvtColor(result_image, cv2.COLOR_RGB2BGR)

    # Convert NumPy array directly to bytes
    success, encoded_img = cv2.imencode(".png", result_image_rgb)
    if not success:
        raise ValueError("Could not encode image")

    return Response(content=encoded_img.tobytes(), media_type="image/png")
