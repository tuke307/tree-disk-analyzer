import cv2
import numpy as np
import os
import logging
from pathlib import Path
from typing import List, Tuple

from treedisksegmentation.utils.file_utils import save_image
from ..config import config

logger = logging.getLogger(__name__)


def apply_mask(image: np.ndarray, masks: List[np.ndarray]) -> np.ndarray:
    """
    Applies the provided polygon masks to the image, isolating the tree disk regions
    against a white background.

    Args:
        image (np.ndarray): The input image in BGR format
        masks (List[np.ndarray]): List of polygon coordinates for each detected object

    Returns:
        np.ndarray: The resulting image with masked objects on white background
    """
    height, width = image.shape[:2]
    masked_output = np.ones((height, width, 3), dtype=np.uint8) * 255

    for mask in masks:
        mask = mask.astype(int)
        mask_img = np.zeros_like(image)

        cv2.fillPoly(mask_img, [mask], (255, 255, 255))
        masked_object = cv2.bitwise_and(image, mask_img)
        masked_output[mask_img == 255] = masked_object[mask_img == 255]

    if config.save_results:
        output_path = Path(config.output_dir)
        output_image_path = os.path.join(output_path, "output.jpg")

        save_image(output_image_path, masked_output)
        logger.info(f"Result image saved at: {output_image_path}")

    return masked_output
