from fastapi import APIRouter, Response, UploadFile, File
import treedisksegmentation
from PIL import Image
import io
from io import BytesIO
import logging

from ...config.settings import (
    OUTPUT_DIR,
    INPUT_DIR,
    U2NET_MODEL_PATH,
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
        model_path=U2NET_MODEL_PATH,
        output_dir=OUTPUT_DIR,
        save_results=SAVE_RESULTS,
        debug=DEBUG,
    )
    result_image, mask_original_dim = treedisksegmentation.run()

    # Convert the NumPy array to a PIL Image
    pil_image = Image.fromarray(result_image.astype("uint8"))

    # Save the PIL Image to a BytesIO object
    img_byte_arr = BytesIO()
    pil_image.save(img_byte_arr, format="PNG")
    img_byte_arr.seek(0)

    # Return the image as a response
    return Response(content=img_byte_arr.getvalue(), media_type="image/png")
