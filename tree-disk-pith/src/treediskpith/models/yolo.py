from cv2 import log
import numpy as np
from ultralytics import YOLO
from typing import Tuple, Union
import logging
from PIL import Image

from ..config import config

logger = logging.getLogger(__name__)


def run_yolo_detection(img_in: np.ndarray) -> Tuple[int, int]:
    """
    Adaptive Pith Detection using Deep Learning model.

    Args:
        img_in (np.ndarray): Input image.
        output_dir (str): Directory to save outputs.
        model_path (str or str): Path to the trained model weights.

    Returns:
        np.ndarray: Detected center point coordinates.
    """
    if config.model_path is None:
        raise ValueError("model_path is None")

    # yolo needs the image as a PIL image
    img_pil = Image.fromarray(img_in)

    model = YOLO(
        config.model_path,
        task="detect",
        verbose=config.debug,
    )
    results = model(
        img_pil,
        project=config.output_dir,
        save=config.save_results,
    )

    if not results or len(results) == 0:
        raise ValueError("No pith detected in the image")

    logger.debug(f"results {results}")

    # just use the first result
    result = results[0]

    logger.info(f"result {result}")

    # xywh = result.boxes.xywh  # center-x, center-y, width, height
    # xywhn = result.boxes.xywhn  # normalized
    # xyxy = result.boxes.xyxy  # top-left-x, top-left-y, bottom-right-x, bottom-right-y
    # xyxyn = result.boxes.xyxyn  # normalized
    # names = [result.names[cls.item()] for cls in result.boxes.cls.int()]  # class name of each box
    # confs = result.boxes.conf  # confidence score of each box

    # Get first detection's center coordinates directly from results
    boxes = result.boxes

    if len(boxes) > 0:
        # Get exact floating point coordinates for better precision
        cx = int(boxes[0].xywh[0][0].item())  # Center x-coordinate
        cy = int(boxes[0].xywh[0][1].item())  # Center y-coordinate
    else:
        raise ValueError("No pith detected in the image")

    logger.info(f"cx {cx}, cy {cy}")

    return (cx, cy)
