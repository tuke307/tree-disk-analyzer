import logging
import numpy as np
from ultralytics import YOLO
from typing import Union, Optional, List, Dict
from pathlib import Path

from ..config import config

logger = logging.getLogger(__name__)


def run_yolo_detection(img_in: np.ndarray) -> dict:
    """
    Uses a YOLO detection model to perform object detection on the input image.

    Args:
        img_in (np.ndarray): Input image.
        output_dir (str): Directory to save outputs (if enabled).
        model_path (str): Path to the trained model weights.

    Returns:
        dict: Detection results in JSON format.
    """
    if config.model_path is None:
        raise ValueError("model_path is None")

    model = YOLO(config.model_path, task="detect", verbose=config.debug)

    results = model(
        img_in,
        project=config.output_dir,
        save=config.save_results,
        save_txt=config.save_results,
    )

    logger.info("YOLO detection complete")
    logger.info(f"Results: {results}")

    result_json = results[0].to_json() if hasattr(results[0], "to_json") else results[0]
    if "predictions" not in result_json or not result_json["predictions"]:
        raise ValueError("No predictions found in YOLO result")

    return result_json


def get_polygon_points(
    detections: dict, class_name: str = "logs"
) -> Optional[List[Dict[str, float]]]:
    """
    Extracts polygon points from the detections for the specified class.

    Args:
        detections (dict): Detection results in JSON format.
        class_name (str): The class name to filter predictions (default "logs").

    Returns:
        Optional[List[Dict[str, float]]]: The list of polygon points if found, otherwise None.
    """
    for prediction in detections["predictions"]:
        if prediction.get("class", "").lower() == class_name.lower():
            return prediction.get("points", None)
    return None
