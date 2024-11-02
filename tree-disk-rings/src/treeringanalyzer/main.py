import logging
from pathlib import Path
import time

from .utils.file_utils import load_image, write_json
from .analyzer import tree_ring_detection
from .config import config
from .utils.results_handler import save_results, chain_to_labelme

logger = logging.getLogger(__name__)


def run_tree_ring_detection() -> int:
    """
    Main function to run tree ring detection.

    Args:
        None

    Returns:
        int: Exit code.
    """
    # Set up logging based on debug setting
    logging.basicConfig(
        level=logging.DEBUG if config.debug else logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    config.log_configurations()

    try:
        # Load input image
        logger.info(f"Loading input image: {config.input_image_path}")
        img_in = load_image(config.input_image_path)

        logger.info("Running tree ring detection...")

        start_time = time.time()

        results = tree_ring_detection(img_in)

        exec_time = time.time() - start_time

        # Save all results
        logger.info("Saving results...")
        save_results(results, config)

        # Save configuration copy
        config_path = config.output_dir / "config.json"
        write_json(config.to_dict(), config_path)
        logger.info(f"Saved configuration to {config_path}")

        logger.info(f"Processing completed in {exec_time:.2f} seconds")
        return 0

    except Exception as e:
        logger.error(f"Error during processing: {str(e)}", exc_info=True)
        return 1
