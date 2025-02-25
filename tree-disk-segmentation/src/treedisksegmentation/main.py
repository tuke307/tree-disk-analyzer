import os
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import numpy as np
from PIL import Image

from .config import config
from .models.yolo import run_yolo_detection
from .utils.file_utils import load_image, save_image
from .segmentation.segmentation import (
    apply_mask,
)

logger = logging.getLogger(__name__)


def run() -> Tuple[np.ndarray, Optional[List[np.ndarray]]]:
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
        img_in = load_image(str(config.input_image))

        logger.info("Running YOLO object segmentation...")
        masks = run_yolo_detection(img_in)

        if not masks:
            return np.array([]), None

        logger.info("Applying mask to original image...")
        result_image = apply_mask(img_in, masks)

        logger.debug(f"Done.")

        return result_image, masks

    except Exception as e:
        logger.error(f"Error during processing: {str(e)}", exc_info=True)
        return np.array([]), None
