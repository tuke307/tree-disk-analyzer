import logging
import time
from typing import Tuple, List
import numpy as np


from .utils.file_utils import load_image, write_json
from .analyzer import tree_ring_detection
from .config import config
from .utils.results_handler import save_results
from .geometry.curve import Curve
from .geometry.chain import Chain

logger = logging.getLogger(__name__)


def run() -> Tuple[
    np.ndarray,
    np.ndarray,
    np.ndarray,
    List[Curve],
    List[Chain],
    List[Chain],
    List[Chain],
]:
    """
    Main function to run tree ring detection.

    Args:
        None

    Returns:
        Tuple containing:
            - img_in (np.ndarray): Original input image.
            - img_pre (np.ndarray): Preprocessed image.
            - devernay_curves (np.ndarray): Devernay curves in matrix format.
            - devernay_curves_f (List[Curve]): Filtered Devernay curves.
            - devernay_curves_s (List[Chain]): Sampled Devernay curves as Chain objects.
            - devernay_curves_c (List[Chain]): Chain lists after connect stage.
            - devernay_curves_p (List[Chain]): Chain lists after postprocessing stage.
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
        ) = tree_ring_detection(img_in)

        exec_time = time.time() - start_time

        if config.save_results:
            logger.info("Saving results...")
            save_results(
                img_in,
                img_pre,
                devernay_edges,
                devernay_curves_f,
                devernay_curves_s,
                devernay_curves_c,
                devernay_curves_p,
            )

            config_path = config.output_dir / "config.json"
            write_json(config.to_dict(), config_path)
            logger.info(f"Saved configuration to {config_path}")

        logger.info(f"Processing completed in {exec_time:.2f} seconds")
        return (
            img_in,
            img_pre,
            devernay_edges,
            devernay_curves_f,
            devernay_curves_s,
            devernay_curves_c,
            devernay_curves_p,
        )

    except Exception as e:
        logger.error(f"Error during processing: {str(e)}", exc_info=True)
        return None
