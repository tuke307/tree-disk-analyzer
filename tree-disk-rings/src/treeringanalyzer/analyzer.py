import time
import numpy as np
from typing import List, Tuple, Dict, Any
from .geometry.curve import Curve
from .geometry.chain import Chain
from .utils.file_utils import chain_2_labelme_json
from .processing.preprocessing import preprocessing
from .detection.canny_devernay_edge_detector import canny_deverney_edge_detector
from .detection.filter_edges import filter_edges
from .processing.sampling import sampling_edges
from .analysis.connect_chains import connect_chains
from .processing.postprocessing import postprocessing


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

    im_pre, cy, cx = preprocessing(im_in, height, width, cy, cx)
    m_ch_e, gx, gy = canny_deverney_edge_detector(im_pre, sigma, th_low, th_high)
    l_ch_f = filter_edges(m_ch_e, cy, cx, gx, gy, alpha, im_pre)
    l_ch_s, l_nodes_s = sampling_edges(
        l_ch_f, cy, cx, im_pre, mc, nr, debug, debug_output_dir
    )
    l_ch_c, l_nodes_c = connect_chains(
        l_ch_s, cy, cx, nr, debug, im_pre, debug_output_dir
    )
    l_ch_p = postprocessing(l_ch_c, l_nodes_c, debug, debug_output_dir, im_pre)

    execution_time = time.time() - start_time

    labelme_json = chain_2_labelme_json(
        l_ch_p,
        height,
        width,
        cy,
        cx,
        im_in,
        f"../{debug_image_input_path}",
        execution_time,
    )

    return im_in, im_pre, m_ch_e, l_ch_f, l_ch_s, l_ch_c, l_ch_p, labelme_json
