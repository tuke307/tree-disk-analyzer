import os
import logging
from pathlib import Path
from typing import Tuple
import numpy as np

from .config import config
from .models.utils import load_model
from .utils.file_utils import load_image, save_image
from .segmentation.segmentation import (
    salient_object_detection,
    apply_mask,
    preprocess_image,
)

logger = logging.getLogger(__name__)


def run() -> Tuple[np.ndarray, np.ndarray]:
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

        logger.info("Loading model...")
        model = load_model(config.model_path)

        logger.info("Preprocessing image...")
        image_tensor, original_size, original_image = preprocess_image(img_in)

        logger.info("Running salient object detection...")
        mask = salient_object_detection(model, image_tensor)

        logger.info("Applying mask to original image...")
        result_image, mask_original_dim = apply_mask(
            original_image, mask, original_size
        )

        if config.save_results:
            output_path = Path(config.output_dir)
            output_image_path = os.path.join(output_path, "output.jpg")

            save_image(output_image_path, result_image)
            logger.info(f"Result image saved at: {output_image_path}")

        logger.debug(f"Done.")

        return result_image, mask_original_dim

    except Exception as e:
        logger.error(f"Error during processing: {str(e)}", exc_info=True)
        return None
