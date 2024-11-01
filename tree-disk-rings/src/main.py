import logging
from pathlib import Path
from .utils.file_utils import load_image, clear_dir, save_config, saving_results
from .analyzer import tree_ring_detection

logger = logging.getLogger(__name__)


def run_tree_ring_detection(
    input_image_path: str,
    output_dir: str,
    cx: int,
    cy: int,
    sigma: float = 3.0,
    th_low: float = 5.0,
    th_high: float = 20.0,
    height: int = 0,
    width: int = 0,
    alpha: float = 30.0,
    nr: int = 360,
    mc: int = 2,
    debug: bool = False,
    save_imgs: bool = False,
    root_dir: str = "./",
) -> int:
    """
    Main function to run tree ring detection.

    Args:
        input_image_path (str): Path to input image.
        output_dir (str): Path to output directory.
        cx (int): Pith x-coordinate.
        cy (int): Pith y-coordinate.
        sigma (float): Canny edge detector Gaussian kernel parameter.
        th_low (float): Low threshold on the module of the gradient.
        th_high (float): High threshold on the module of the gradient.
        height (int): Height of the image after the resize step.
        width (int): Width of the image after the resize step.
        alpha (float): Edge filtering parameter (collinearity threshold).
        nr (int): Number of rays.
        mc (int): Minimum chain length.
        debug (bool): Debug mode.
        save_imgs (bool): Whether to save intermediate images.
        root_dir (Optional[str]): Root directory of the repository.

    Returns:
        int: Exit code.
    """
    config = {
        "input_image_path": input_image_path,
        "output_dir": output_dir,
        "cx": cx,
        "cy": cy,
        "sigma": sigma,
        "th_low": th_low,
        "th_high": th_high,
        "height": height,
        "width": width,
        "alpha": alpha,
        "nr": nr,
        "mc": mc,
        "debug": debug,
        "save_imgs": save_imgs,
        "root_dir": root_dir,
    }

    if debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    logger.info("Configuration:")
    for key, value in config.items():
        logger.info(f"{key}: {value}")

    save_config(config, root_dir, output_dir)

    im_in = load_image(input_image_path)
    if im_in is None:
        raise FileNotFoundError(f"Input image '{input_image_path}' not found.")

    Path(output_dir).mkdir(exist_ok=True, parents=True)
    clear_dir(output_dir)

    result = tree_ring_detection(
        im_in,
        cy,
        cx,
        sigma,
        th_low,
        th_high,
        height,
        width,
        alpha,
        nr,
        mc,
        debug,
        input_image_path,
        output_dir,
    )

    saving_results(result, output_dir, save_imgs)

    return 0
