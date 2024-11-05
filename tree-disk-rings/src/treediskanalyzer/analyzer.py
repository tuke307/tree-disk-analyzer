import numpy as np
import cv2
from typing import List, Tuple, Dict, Any
from .geometry.curve import Curve
from .geometry.chain import Chain
from .processing.preprocessing import preprocessing
from .detection.canny_devernay_edge_detector import canny_deverney_edge_detector
from .detection.filter_edges import filter_edges
from .processing.sampling import sampling_edges
from .analysis.connect_chains import connect_chains
from .processing.postprocessing import postprocessing
from .config import config


def tree_ring_detection(img_in: cv2.typing.MatLike) -> Tuple[
    np.ndarray,
    np.ndarray,
    np.ndarray,
    List[Curve],
    List[Chain],
    List[Chain],
    List[Chain],
]:
    """
    Delineate tree rings over pine cross-section images. Implements Algorithm 1 from the paper.

    Args:
        img_in (cv2.typing.MatLike): Segmented input image. Background must be white (255,255,255).

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
    img_pre = preprocessing(img_in)

    devernay_result_c = canny_deverney_edge_detector(
        img_pre, sigma=config.sigma, low=config.th_low, high=config.th_high
    )

    devernay_edges, gradient_x_img, gradient_y_img = devernay_result_c

    devernay_curves_f = filter_edges(
        devernay_edges, gradient_x_img, gradient_y_img, img_pre
    )
    devernay_curves_s, l_nodes_s = sampling_edges(devernay_curves_f, img_pre)
    devernay_curves_c, l_nodes_c = connect_chains(devernay_curves_s, img_pre)
    devernay_curves_p = postprocessing(devernay_curves_c, l_nodes_c, img_pre)

    return (
        img_in,
        img_pre,
        devernay_edges,
        devernay_curves_f,
        devernay_curves_s,
        devernay_curves_c,
        devernay_curves_p,
    )
