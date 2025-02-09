from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
import treediskpith
from PIL import Image
import io

from config import OUTPUT_DIR, INPUT_DIR, YOLO_MODEL_PATH, DEBUG, SAVE_RESULTS

router = APIRouter()


@router.post(
    "/detect",
    responses={
        429: {"description": "Too Many Requests"},
    },
)
async def detect_pith(
    image: UploadFile = File(...),
) -> None:
    """
    Detect the pith in the image.<br>
    """
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
        method="apd_dl",
        save_results=SAVE_RESULTS,
        debug=DEBUG,
    )
    img_in, img_processed, pith = treediskpith.run()

    data = {
        "x": int(pith[0]),
        "y": int(pith[1]),
    }

    # return pith tuple
    return JSONResponse(content=data)
