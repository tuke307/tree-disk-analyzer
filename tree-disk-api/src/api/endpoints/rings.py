from fastapi import APIRouter, Response, UploadFile, File, HTTPException
import treediskrings
from PIL import Image
import io
from io import BytesIO
import logging

from ...config.settings import OUTPUT_DIR, INPUT_DIR, DEBUG, SAVE_RESULTS

router = APIRouter()
logger = logging.getLogger(__name__)


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

    (
        img_in,
        img_pre,
        devernay_edges,
        devernay_curves_f,
        devernay_curves_s,
        devernay_curves_c,
        devernay_curves_p,
    ) = treediskrings.run()

    # read the output image OUTPUT_DIR/output.png
    output_path = OUTPUT_DIR / "output.png"
    pil_image = Image.open(output_path)

    # Save the PIL Image to a BytesIO object
    img_byte_arr = BytesIO()
    pil_image.save(img_byte_arr, format="PNG")
    img_byte_arr.seek(0)

    # Return the image as a response
    return Response(content=img_byte_arr.getvalue(), media_type="image/png")
