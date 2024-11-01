import argparse
import time
from pathlib import Path
from typing import Any, List, Optional, Tuple, Dict
import logging
import numpy as np

from src.geometry.curve import Curve
from src.geometry.chain import Chain
from src.utils.file_utils import load_image, clear_dir
from src.processing.preprocessing import preprocessing
from src.detection.canny_devernay_edge_detector import canny_deverney_edge_detector
from src.detection.filter_edges import filter_edges
from src.processing.sampling import sampling_edges
from src.analysis.connect_chains import connect_chains
from src.processing.postprocessing import postprocessing
from src.utils.file_utils import chain_2_labelme_json, save_config, saving_results

logger = logging.getLogger(__name__)


def tree_ring_detection(
    im_in: np.ndarray,
    cy: int,
    cx: int,
    sigma: float,
    th_low: float,
    th_high: float,
    height: int,
    width: int,
    alpha: float,
    nr: int,
    mc: int,
    debug: bool,
    debug_image_input_path: str,
    debug_output_dir: str,
) -> Tuple[
    np.ndarray,
    np.ndarray,
    np.ndarray,
    List[Curve],
    List[Chain],
    List[Chain],
    List[Chain],
    Dict[str, Any],
]:
    """
    Delineate tree rings over pine cross-section images. Implements Algorithm 1 from the paper.

    Args:
        im_in (np.ndarray): Segmented input image. Background must be white (255,255,255).
        cy (int): Pith y-coordinate.
        cx (int): Pith x-coordinate.
        sigma (float): Canny edge detector Gaussian kernel parameter.
        th_low (float): Low threshold on the module of the gradient (Canny edge detector parameter).
        th_high (float): High threshold on the module of the gradient (Canny edge detector parameter).
        height (int): Height of the image after the resize step.
        width (int): Width of the image after the resize step.
        alpha (float): Edge filtering parameter (collinearity threshold).
        nr (int): Number of rays.
        mc (int): Minimum chain length.
        debug (bool): Debug mode.
        debug_image_input_path (str): Path to input image (used to write LabelMe JSON).
        debug_output_dir (str): Output directory where debug results are saved.

    Returns:
        Tuple containing:
            - im_in (np.ndarray): Original input image.
            - im_pre (np.ndarray): Preprocessed image.
            - m_ch_e (np.ndarray): Devernay curves in matrix format.
            - l_ch_f (List[Curve]): Filtered Devernay curves.
            - l_ch_s (List[Chain]): Sampled Devernay curves as Chain objects.
            - l_ch_c (List[Chain]): Chain lists after connect stage.
            - l_ch_p (List[Chain]): Chain lists after postprocessing stage.
            - labelme_json (Dict[str, Any]): Final results (JSON file with rings coordinates).
    """
    start_time = time.time()

    # Preprocess the image.
    im_pre, cy, cx = preprocessing(im_in, height, width, cy, cx)

    # Edge detection using Canny-Devernay algorithm.
    m_ch_e, gx, gy = canny_deverney_edge_detector(im_pre, sigma, th_low, th_high)

    # Edge filtering.
    l_ch_f = filter_edges(m_ch_e, cy, cx, gx, gy, alpha, im_pre)

    # Sampling edges.
    l_ch_s, l_nodes_s = sampling_edges(
        l_ch_f, cy, cx, im_pre, mc, nr, debug, debug_output_dir
    )

    # Connect chains.
    l_ch_c, l_nodes_c = connect_chains(
        l_ch_s, cy, cx, nr, debug, im_pre, debug_output_dir
    )

    # Postprocess chains.
    l_ch_p = postprocessing(l_ch_c, l_nodes_c, debug, debug_output_dir, im_pre)

    # Generate final results.
    debug_execution_time = time.time() - start_time
    labelme_json = chain_2_labelme_json(
        l_ch_p,
        height,
        width,
        cy,
        cx,
        im_in,
        f"../{debug_image_input_path}",
        debug_execution_time,
    )

    return im_in, im_pre, m_ch_e, l_ch_f, l_ch_s, l_ch_c, l_ch_p, labelme_json


def main(
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
    root_dir: Optional[str] = "./",
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
    # Save configuration
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

    logger.info("\nConfiguration:")
    for key, value in config.items():
        logger.info(f"{key}: {value}")

    save_config(config, root_dir, output_dir)

    # Load input image
    im_in = load_image(input_image_path)
    if im_in is None:
        raise FileNotFoundError(
            f"Input image '{input_image_path}' not found or could not be loaded."
        )

    Path(output_dir).mkdir(exist_ok=True, parents=True)
    clear_dir(output_dir)

    # Run tree ring detection
    res = tree_ring_detection(
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

    # Save results
    saving_results(res, output_dir, save_imgs)

    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tree Ring Detection")
    parser.add_argument("--input", type=str, required=True, help="Path to input image")
    parser.add_argument("--cx", type=int, required=True, help="Pith x-coordinate")
    parser.add_argument("--cy", type=int, required=True, help="Pith y-coordinate")
    parser.add_argument(
        "--output_dir", type=str, required=True, help="Output directory"
    )
    parser.add_argument(
        "--root", type=str, default="./", help="Root directory of the repository"
    )

    parser.add_argument(
        "--sigma",
        type=float,
        default=3.0,
        help="Gaussian kernel parameter for edge detection",
    )
    parser.add_argument(
        "--th_low", type=float, default=5.0, help="Low threshold for gradient magnitude"
    )
    parser.add_argument(
        "--th_high",
        type=float,
        default=20.0,
        help="High threshold for gradient magnitude",
    )
    parser.add_argument(
        "--height",
        type=int,
        default=0,
        help="Height after resizing (0 to keep original)",
    )
    parser.add_argument(
        "--width", type=int, default=0, help="Width after resizing (0 to keep original)"
    )
    parser.add_argument(
        "--alpha",
        type=float,
        default=30.0,
        help="Edge filtering parameter (collinearity threshold)",
    )
    parser.add_argument("--nr", type=int, default=360, help="Number of rays")
    parser.add_argument(
        "--min_chain_length", type=int, default=2, help="Minimum chain length"
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument(
        "--save_imgs", action="store_true", help="Save intermediate images"
    )

    args = parser.parse_args()

    main(
        input_image_path=args.input,
        output_dir=args.output_dir,
        cx=args.cx,
        cy=args.cy,
        sigma=args.sigma,
        th_low=args.th_low,
        th_high=args.th_high,
        height=args.height,
        width=args.width,
        alpha=args.alpha,
        nr=args.nr,
        mc=args.min_chain_length,
        debug=args.debug,
        save_imgs=args.save_imgs,
        root_dir=args.root,
    )
