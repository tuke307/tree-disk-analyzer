import logging
import numpy as np
from ultralytics import YOLO
from typing import Union, Optional, List, Dict
from pathlib import Path
from PIL import Image

from ..config import config

logger = logging.getLogger(__name__)


def run_yolo_detection(img_in: np.ndarray) -> Optional[List[np.ndarray]]:
    """
    Uses a YOLO detection model to perform object detection on the input image.

    Args:
        img_in (np.ndarray): Input image.
        output_dir (str): Directory to save outputs (if enabled).
        model_path (str): Path to the trained model weights.

    Returns:
        Optional[List[np.ndarray]]: The detected object masks as a list of polygons.
    """
    if config.model_path is None:
        raise ValueError("model_path is None")

    # yolo needs the image as a PIL image
    img_pil = Image.fromarray(img_in)

    model = YOLO(config.model_path, task="detect", verbose=config.debug)

    results = model(
        img_pil,
        project=config.output_dir,
        save=config.save_results,
        save_txt=config.save_results,
    )

    logger.info(f"YOLO detection complete.")

    if not results or len(results) == 0:
        logger.error("No results found in YOLO detection.")
        return None

    # were just using the first result
    first_result = results[0]

    # xy = first_result.masks.xy  # mask in polygon format
    # xyn = first_result.masks.xyn  # normalized
    # masks = first_result.masks.data  # mask in matrix format (num_objects x H x W)

    if first_result.masks is not None and first_result.masks.xy is not None:
        return first_result.masks.xy
    else:
        logger.warning("No mask polygons found in the YOLO result.")
        return None
