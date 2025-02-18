import logging
import time
from typing import Tuple, List
import numpy as np


from .utils.file_utils import load_image, write_json
from .analyzer import tree_ring_detection, tree_ring_detection_age_detect
from .config import config
from .utils.results_handler import save_results
from .geometry.curve import Curve
from .geometry.chain import Chain

logger = logging.getLogger(__name__)


def run() -> Tuple[
    int,
    np.ndarray,
]:
    """
    Main function to run tree ring detection.

    Args:
        None

    Returns:
        Tuple containing:
            - average_ring_count (int): Average ring count.
            - output visualization (np.ndarray): Output visualization image.
    """
    # Set up logging based on debug setting
    logging.basicConfig(
        level=logging.DEBUG if config.debug else logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    try:
        config.log_all_configs()

        logger.info(f"Loading input image: {config.input_image}")

        if config.input_image is None:
            raise ValueError("Input image path cannot be None")

        img_in = load_image(config.input_image)

        logger.info("Running tree ring detection...")

        start_time = time.time()

        (
            img_in,
            img_pre,
            devernay_edges,
            devernay_curves_f,
            devernay_curves_s,
            devernay_curves_c,
            devernay_curves_p,
            average_ring_count,
        ) = tree_ring_detection(img_in)

        exec_time = time.time() - start_time

        # Get visualizations (and optionally save them)
        vis_images = save_results(
            img_in,
            img_pre,
            devernay_edges,
            devernay_curves_f,
            devernay_curves_s,
            devernay_curves_c,
            devernay_curves_p,
            save_to_disk=config.save_results,
        )

        # Save configuration if requested
        if config.save_results:
            config_path = config.output_dir / "config.json"
            write_json(config.to_dict(), config_path)
            logger.info(f"Saved configuration to {config_path}")

        logger.info(f"Processing completed in {exec_time:.2f} seconds")

        return (
            average_ring_count,
            vis_images["output"],
        )

    except Exception as e:
        logger.error(f"Error during processing: {str(e)}", exc_info=True)
        return (
            0,
            np.array([]),
        )


def run_age_detect() -> Tuple[int, np.ndarray]:
    """
    Main function to run simplified tree ring age detection.

    Returns:
        Tuple containing:
            - ring_count (int): Number of detected rings.
            - output visualization (np.ndarray): Debug image showing detected curves.
    """
    logging.basicConfig(
        level=logging.DEBUG if config.debug else logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    try:
        config.log_all_configs()
        logger.info(f"Loading input image: {config.input_image}")

        if config.input_image is None:
            raise ValueError("Input image path cannot be None")

        img_in = load_image(config.input_image)
        logger.info("Running tree ring age detection...")

        start_time = time.time()
        (
            img_in,
            img_pre,
            devernay_edges,
            devernay_curves_f,
            devernay_curves_s,
            ring_count,
        ) = tree_ring_detection_age_detect(img_in)

        exec_time = time.time() - start_time

        # Get visualizations (and optionally save them)
        vis_images = save_results(
            img_in,
            img_pre,
            devernay_edges,
            devernay_curves_f,
            devernay_curves_s,
            save_to_disk=config.save_results,
        )

        if config.save_results:
            config_path = config.output_dir / "config.json"
            write_json(config.to_dict(), config_path)
            logger.info(f"Saved configuration to {config_path}")

        logger.info(f"Processing completed in {exec_time:.2f} seconds")
        logger.info(f"Detected rings: {ring_count}")

        return ring_count, vis_images["filter"]

    except Exception as e:
        logger.error(f"Error during processing: {str(e)}", exc_info=True)
        return 0, np.array([])
