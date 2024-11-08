from fastapi import APIRouter, Response, UploadFile, File, HTTPException
from typing import List
import treediskrings
from PIL import Image
import io
import numpy as np
from io import BytesIO

from ...config import OUTPUT_DIR, INPUT_DIR

router = APIRouter()


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
) -> None:
    """
    Detect the rings in the image.<br>
    """
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
        save_results=True,
    )
    results = treediskrings.run()

    # read the output image OUTPUT_DIR/output.png
    output_path = OUTPUT_DIR / "output.png"
    pil_image = Image.open(output_path)

    # Save the PIL Image to a BytesIO object
    img_byte_arr = BytesIO()
    pil_image.save(img_byte_arr, format="PNG")
    img_byte_arr.seek(0)

    # Return the image as a response
    return Response(content=img_byte_arr.getvalue(), media_type="image/png")
