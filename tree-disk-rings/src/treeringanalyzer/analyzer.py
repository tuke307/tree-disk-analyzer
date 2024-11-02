import time
import numpy as np
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


def tree_ring_detection(img_in: np.ndarray) -> Tuple[
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
        img_in (np.ndarray): Segmented input image. Background must be white (255,255,255).

    Returns:
        Tuple containing:
            - img_in (np.ndarray): Original input image.
            - im_pre (np.ndarray): Preprocessed image.
            - m_ch_e (np.ndarray): Devernay curves in matrix format.
            - l_ch_f (List[Curve]): Filtered Devernay curves.
            - l_ch_s (List[Chain]): Sampled Devernay curves as Chain objects.
            - l_ch_c (List[Chain]): Chain lists after connect stage.
            - l_ch_p (List[Chain]): Chain lists after postprocessing stage.
    """
    im_pre, cy, cx = preprocessing(
        img_in, config.height, config.width, config.cy, config.cx
    )
    m_ch_e, gx, gy = canny_deverney_edge_detector(
        im_pre, config.sigma, config.th_low, config.th_high
    )
    l_ch_f = filter_edges(m_ch_e, cy, cx, gx, gy, config.alpha, im_pre)
    l_ch_s, l_nodes_s = sampling_edges(
        l_ch_f, cy, cx, im_pre, config.mc, config.nr, config.debug, config.output_dir
    )
    l_ch_c, l_nodes_c = connect_chains(
        l_ch_s, cy, cx, config.nr, config.debug, im_pre, config.output_dir
    )
    l_ch_p = postprocessing(l_ch_c, l_nodes_c, config.debug, config.output_dir, im_pre)

    return img_in, im_pre, m_ch_e, l_ch_f, l_ch_s, l_ch_c, l_ch_p
