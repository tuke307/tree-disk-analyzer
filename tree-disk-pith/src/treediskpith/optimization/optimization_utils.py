import numpy as np
import cv2
from typing import Optional, Tuple, Any

from ..visualization.color import Color
from ..visualization.drawing import Shapes


def filter_lo_around_c(
    Lof: np.ndarray, rf: float, ci: Tuple[float, float], img_in: np.ndarray
) -> Tuple[np.ndarray, Tuple[float, float], Tuple[float, float]]:
    """
    Filters lines around a central point within a region defined by a reduction factor.

    Args:
        Lof: Array of line segments of shape (N, 4).
        rf: Reduction factor to define the region size.
        ci: Central point coordinates (x, y).
        img_in: Input image array.

    Returns:
        A tuple containing:
            - m_lines_within_region: Array of lines within the defined region.
            - top_left: Coordinates of the top-left corner of the region.
            - bottom_right: Coordinates of the bottom-right corner of the region.
    """
    x, y = ci
    H, W = img_in.shape[:2]
    # Define region
    top_left = (x - W / rf, y - H / rf)
    bottom_right = (x + W / rf, y + H / rf)

    m_lines_within_region, _ = get_lines_idx_within_rectangular_region(
        img_in,
        Lof,
        None,
        int(top_left[0]),
        int(top_left[1]),
        int(bottom_right[0]),
        int(bottom_right[1]),
        debug=False,
        output_path=None,
    )
    return m_lines_within_region, top_left, bottom_right


def get_lines_idx_within_rectangular_region(
    img_in: np.ndarray,
    L: np.ndarray,
    weights: Optional[np.ndarray],
    top_x: int,
    top_y: int,
    bottom_x: int,
    bottom_y: int,
    debug: bool,
    output_path: Optional[str] = None,
) -> Tuple[np.ndarray, Optional[np.ndarray]]:
    """
    Gets indices of lines within a rectangular region.

    Args:
        img_in: Input image array.
        L: Array of line segments of shape (N, 4).
        weights: Optional array of weights corresponding to the lines.
        top_x: Top-left x-coordinate of the region.
        top_y: Top-left y-coordinate of the region.
        bottom_x: Bottom-right x-coordinate of the region.
        bottom_y: Bottom-right y-coordinate of the region.
        debug: Flag to enable debug mode.
        output_path: Optional path to save debug images.

    Returns:
        A tuple containing:
            - l_lines_within_region: Array of lines within the region.
            - weights_within_region: Weights corresponding to the lines within the region.
    """
    X1, Y1, X2, Y2 = L[:, 0], L[:, 1], L[:, 2], L[:, 3]

    X_min = np.minimum(X1, X2)
    X_max = np.maximum(X1, X2)
    Y_min = np.minimum(Y1, Y2)
    Y_max = np.maximum(Y1, Y2)

    idx = np.where(
        (top_x <= X_min) & (X_max <= bottom_x) & (top_y <= Y_min) & (Y_max <= bottom_y)
    )[0]
    l_lines_within_region = L[idx]
    weights_within_region = weights[idx] if weights is not None else None

    if debug:
        # Draw rectangular region
        img = img_in.copy()
        img = cv2.rectangle(img, (top_x, top_y), (bottom_x, bottom_y), Color.black, 2)
        Shapes.draw_lsd_lines(
            l_lines_within_region, img, output_path=output_path, lines_all=L
        )

    return l_lines_within_region, weights_within_region
