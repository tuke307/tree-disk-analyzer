import time
from pathlib import Path
from typing import Optional, Tuple
import logging
import cv2
import numpy as np
import pandas as pd

from .visualization.color import Color
from .processing.image_processing import resize_image_using_pil_lib
from .detection.pith_detection import apd, apd_pcl, apd_dl
from .detection.detection_method import DetectionMethod
from .utils.file_utils import write_json, save_image
from .config import config

logger = logging.getLogger(__name__)


def tree_disk_pith_detector(img_in: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Detect tree disk pith using configured method.

    Args:
        img_in (np.ndarray): Input image

    Returns:
        Tuple: (processed_image, detected_pith_coordinates)
    """
    original_height, original_width = img_in.shape[:2]
    img_processed = img_in.copy()

    # Resize image if needed
    if config.new_shape > 0:
        img_processed = resize_image_using_pil_lib(
            img_processed, height_output=config.new_shape, width_output=config.new_shape
        )

    if config.save_results:
        path = str(Path(config.output_dir) / "resized.png")
        save_image(img_processed, path)

    # Select and run detection method
    detection_methods = {
        DetectionMethod.APD: lambda: apd(
            img_processed,
            config.st_sigma,
            config.st_w,
            config.lo_w,
            rf=7,
            percent_lo=config.percent_lo,
            max_iter=11,
            epsilon=1e-3,
            debug=config.debug,
            output_dir=config.output_dir,
        ),
        DetectionMethod.APD_PCL: lambda: apd_pcl(
            img_processed,
            config.st_sigma,
            config.st_w,
            config.lo_w,
            rf=7,
            percent_lo=config.percent_lo,
            max_iter=11,
            epsilon=1e-3,
            debug=config.debug,
            output_dir=config.output_dir,
        ),
        DetectionMethod.APD_DL: lambda: apd_dl(
            img_processed, config.output_dir, config.model_path
        ),
    }

    pith = detection_methods[config.method]()

    # Handle debug visualization
    if config.save_results:
        img_with_pith = img_processed.copy()
        height, width = img_with_pith.shape[:2]
        dot_size = max(height // 200, 1)
        x, y = pith
        cv2.circle(
            img_with_pith,
            (int(round(x)), int(round(y))),
            dot_size,
            Color.blue,
            -1,
        )

        path = str(Path(config.output_dir) / "pith.png")
        save_image(img_with_pith, path)

    # Scale coordinates back to original image size if needed
    if config.new_shape > 0:
        new_height, new_width = img_processed.shape[:2]
        scale_x = original_width / new_width
        scale_y = original_height / new_height
        pith = np.array(pith) * np.array([scale_x, scale_y])

    # Save pith
    if config.save_results:
        path = str(Path(config.output_dir) / "pith.json")
        data = {
            "coarse_x": int(pith[0]),
            "coarse_y": int(pith[1]),
        }
        write_json(data, path)

    return img_processed, pith
