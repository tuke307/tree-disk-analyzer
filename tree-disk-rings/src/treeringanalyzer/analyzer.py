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
            - m_ch_e (np.ndarray): Devernay curves in matrix format.
            - l_ch_f (List[Curve]): Filtered Devernay curves.
            - l_ch_s (List[Chain]): Sampled Devernay curves as Chain objects.
            - l_ch_c (List[Chain]): Chain lists after connect stage.
            - l_ch_p (List[Chain]): Chain lists after postprocessing stage.
    """
    img_pre = preprocessing(img_in)

    devernay_result_c = canny_deverney_edge_detector(
        img_pre, sigma=config.sigma, low=config.th_low, high=config.th_high
    )

    devernay_edges, gradient_x_img, gradient_y_img = devernay_result_c

    l_ch_f = filter_edges(devernay_edges, gradient_x_img, gradient_y_img, img_pre)
    l_ch_s, l_nodes_s = sampling_edges(l_ch_f, img_pre)
    l_ch_c, l_nodes_c = connect_chains(l_ch_s, img_pre)
    l_ch_p = postprocessing(l_ch_c, l_nodes_c, img_pre)

    return img_in, img_pre, devernay_edges, l_ch_f, l_ch_s, l_ch_c, l_ch_p
