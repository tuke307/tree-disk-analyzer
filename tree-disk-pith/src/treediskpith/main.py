from typing import Optional, Tuple
import logging
import numpy as np
from pathlib import Path

from .detector import tree_disk_pith_detector
from .config import config
from .utils.file_utils import load_image, write_json

logger = logging.getLogger(__name__)


def run() -> Tuple[
    np.ndarray,
    np.ndarray,
]:
    """
    Main function to run tree ring detection.

    Args:
        None

    Returns:
        Tuple containing:
            - img_in (np.ndarray): Original input image.
            - img_pre (np.ndarray): Preprocessed image.
            - pith (np.ndarray): Detected pith coordinates.
    """
    # Set up logging based on debug setting
    logging.basicConfig(
        level=logging.DEBUG if config.debug else logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    try:
        config.log_all_configs()

        logger.info(f"Loading input image: {config.input_image}")
        img_in = load_image(config.input_image)

        logger.info("Running tree disk pith detection...")
        img_processed, pith = tree_disk_pith_detector(img_in)

        if config.save_results:
            config_path = Path(config.output_dir) / "config.json"
            write_json(config.to_dict(), config_path)
            logger.info(f"Saved configuration to {config_path}")

        return img_in, img_processed, pith

    except Exception as e:
        logger.error(f"Error during processing: {str(e)}", exc_info=True)
        return None
