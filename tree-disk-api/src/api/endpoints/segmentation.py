from fastapi import APIRouter, Response, UploadFile, File, HTTPException
from typing import List
import treedisksegmentation
from PIL import Image
import io
from io import BytesIO

from ...config import OUTPUT_DIR, INPUT_DIR, U2NET_MODEL_PATH

router = APIRouter()


@router.post(
    "/segment",
    responses={
        429: {"description": "Too Many Requests"},
    },
)
async def segment_image(
    image: UploadFile = File(...),
) -> Response:
    """
    Sample endpoint.<br>
    Example usage: http://127.0.0.1:8000/sample
    """
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
        save_results=True,
        debug=True,
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
