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

    if config.debug:
        resized_debug_image = resize_image_using_pil_lib(img_processed, 640, 640)
        cv2.imwrite(str(Path(config.output_dir) / "resized.png"), resized_debug_image)

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
            img_processed, config.output_dir, config.weights_path
        ),
    }

    start_time = time.time()
    pith = detection_methods[config.method]()
    execution_time = time.time() - start_time

    # Handle debug visualization
    if config.debug:
        img_debug = img_processed.copy()
        height, width = img_debug.shape[:2]
        dot_size = max(height // 200, 1)
        x, y = pith
        cv2.circle(
            img_debug,
            (int(round(x)), int(round(y))),
            dot_size,
            Color.blue,
            -1,
        )
        img_debug_resized = resize_image_using_pil_lib(img_debug, 640, 640)
        cv2.imwrite(str(Path(config.output_dir) / "pith.png"), img_debug_resized)

    # Scale coordinates back to original image size if needed
    if config.new_shape > 0:
        new_height, new_width = img_processed.shape[:2]
        scale_x = original_width / new_width
        scale_y = original_height / new_height
        pith = np.array(pith) * np.array([scale_x, scale_y])

    # Save results if enabled
    if config.save_results:
        save_detection_results(pith, execution_time)

    return img_processed, pith


def save_detection_results(pith: np.ndarray, execution_time: float):
    """Save detection results to CSV."""
    data = {
        "coarse_x": [pith[0]],
        "coarse_y": [pith[1]],
        "exec_time(s)": [execution_time],
    }
    df = pd.DataFrame(data)
    df.to_csv(str(Path(config.output_dir) / "pith.csv"), index=False)
