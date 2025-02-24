import os
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import numpy as np
from PIL import Image

from .config import config
from .models.yolo import run_yolo_detection, get_polygon_points
from .utils.file_utils import load_image, save_image
from .segmentation.segmentation import (
    polygon_to_mask,
    apply_mask,
)

logger = logging.getLogger(__name__)


def run() -> Tuple[np.ndarray, Optional[List[Dict[str, float]]]]:
    """
    Pipeline to remove the salient object while maintaining the original resolution.

    Returns:

    """
    logging.basicConfig(
        level=logging.DEBUG if config.debug else logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    try:
        config.log_all_configs()

        logger.info(f"Loading input image: {config.input_image}")
        img_in = load_image(config.input_image)
        img_pil = Image.fromarray(img_in)

        logger.info("Running YOLO object detection...")
        result_json = run_yolo_detection(img_in)

        logger.info("Extracting polygon points...")
        polygon_points = get_polygon_points(result_json)

        if not polygon_points:
            logger.error("No polygon points found in YOLO result.")
            return np.array([]), None

        logger.info("Running salient object detection...")
        mask = polygon_to_mask(img_pil, polygon_points)

        logger.info("Applying mask to original image...")
        result_image, mask_uint8 = apply_mask(img_pil, mask)

        if config.save_results:
            output_path = Path(config.output_dir)
            output_image_path = os.path.join(output_path, "output.jpg")

            save_image(output_image_path, result_image)
            logger.info(f"Result image saved at: {output_image_path}")

        logger.debug(f"Done.")

        return result_image, polygon_points

    except Exception as e:
        logger.error(f"Error during processing: {str(e)}", exc_info=True)
        return np.array([]), None
