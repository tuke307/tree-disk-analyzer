import numpy as np
from ultralytics import YOLO
from typing import Tuple, Union
import logging

from ..config import config

logger = logging.getLogger(__name__)


def apd_dl(
    img_in: np.ndarray, output_dir: str, model_path: Union[str, str]
) -> Tuple[float, float]:
    """
    Adaptive Pith Detection using Deep Learning model.

    Args:
        img_in (np.ndarray): Input image.
        output_dir (str): Directory to save outputs.
        model_path (str or str): Path to the trained model weights.

    Returns:
        np.ndarray: Detected center point coordinates.
    """
    if model_path is None:
        raise ValueError("model_path is None")

    logger.info(f"model_path {model_path}")
    model = YOLO(model_path, task="detect", verbose=config.debug)
    logger.info(f"config {config.save_results}")
    results = model(
        img_in,
        project=output_dir,
        save=config.save_results,
        save_txt=config.save_results,
    )

    # Get first detection's center coordinates directly from results
    boxes = results[0].boxes
    if len(boxes) > 0:
        # Get normalized coordinates and convert to pixel values
        cx = int(boxes[0].xywh[0][0].item())  # Already in pixel coordinates
        cy = int(boxes[0].xywh[0][1].item())  # Already in pixel coordinates
    else:
        raise ValueError("No pith detected in the image")

    return (cx, cy)
