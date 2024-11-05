import numpy as np
from PIL import Image
import cv2
from typing import Tuple, Optional, List

from ..geometry.primitives import Line
from ..visualization.color import Color
from ..optimization.least_squares_solver import LeastSquaresSolution


def compute_intersection_with_block_boundaries(
    p1: Tuple[float, float], p2: Tuple[float, float], img: np.ndarray
) -> Tuple[
    Optional[float],
    Optional[float],
    Optional[float],
    Optional[float],
    Optional[float],
    Optional[float],
    Optional[float],
    Optional[float],
]:
    """
    Computes the intersection points of the line defined by p1 and p2 with the boundaries of the image.

    Args:
        p1: First point as a NumPy array [x, y].
        p2: Second point as a NumPy array [x, y].
        img: The image array.

    Returns:
        A tuple containing intersection points (x1, y1, x2, y2, x3, y3, x4, y4) with the image boundaries.
    """
    # Get the image dimensions
    if img.ndim == 3:
        height, width, _ = img.shape
    else:
        height, width = img.shape

    a, b, c = LeastSquaresSolution.compute_line_coefficients(p1, p2)

    if np.isclose(b, 0) and not np.isclose(a, 0):
        # Vertical line
        x = int(p2[0])
        x1, y1 = x, 0
        x2, y2 = x, height - 1

        return x1, y1, x2, y2, None, None, None, None

    if np.isclose(a, 0) and not np.isclose(b, 0):
        # Horizontal line
        y = int(p2[1])
        x1, y1 = 0, y
        x2, y2 = width - 1, y

        return x1, y1, x2, y2, None, None, None, None

    x1, y1 = 0.0, None
    x2, y2 = float(width - 1), None
    x3, y3 = None, 0.0
    x4, y4 = None, float(height - 1)

    x1, y1 = Line.get_line_coordinates(a, b, c, x=x1)
    x2, y2 = Line.get_line_coordinates(a, b, c, x=x2)
    x3, y3 = Line.get_line_coordinates(a, b, c, y=y3)
    x4, y4 = Line.get_line_coordinates(a, b, c, y=y4)

    return x1, y1, x2, y2, x3, y3, x4, y4


def resize_image_using_pil_lib(
    img_in: np.ndarray, height_output: int, width_output: int, keep_ratio: bool = True
) -> np.ndarray:
    """
    Resizes the image using PIL library.

    Args:
        img_in: Input image as a NumPy array.
        height_output: Desired height of the output image.
        width_output: Desired width of the output image.
        keep_ratio: Whether to maintain the aspect ratio.

    Returns:
        The resized image as a NumPy array.
    """
    pil_img = Image.fromarray(img_in)
    resample_flag = Image.Resampling.LANCZOS

    if keep_ratio:
        aspect_ratio = pil_img.height / pil_img.width
        if pil_img.width > pil_img.height:
            height_output = int(width_output * aspect_ratio)
        else:
            width_output = int(height_output / aspect_ratio)

    pil_img = pil_img.resize((width_output, height_output), resample_flag)
    return np.array(pil_img)


def change_background_to_value(
    img_in: np.ndarray, mask: np.ndarray, value: int = 255
) -> np.ndarray:
    """
    Changes the background intensity to a specified value.

    Args:
        img_in: Input image.
        mask: Mask where non-zero values indicate background.
        value: The intensity value to set for the background.

    Returns:
        The image with background intensity changed.
    """
    img_out = img_in.copy()
    img_out[mask > 0] = value

    return img_out


def rgb2gray(img_r: np.ndarray) -> np.ndarray:
    """
    Converts an RGB image to grayscale.

    Args:
        img_r: Input RGB image.

    Returns:
        Grayscale image.
    """
    return cv2.cvtColor(img_r, cv2.COLOR_BGR2GRAY)


def change_background_intensity_to_mean(
    img_in: np.ndarray,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Changes the background intensity to the mean intensity of the non-background.

    Args:
        img_in: Input grayscale image with background intensity as 255.

    Returns:
        A tuple containing the image with background intensity changed and the background mask.
    """
    im_eq = img_in.copy()
    mask = np.where(img_in == 255, 1, 0)
    mean_intensity = np.mean(img_in[mask == 0])
    im_eq = change_background_to_value(im_eq, mask, int(mean_intensity))
    return im_eq, mask


def equalize_image_using_clahe(img_eq: np.ndarray) -> np.ndarray:
    """
    Equalizes the image using CLAHE algorithm.

    Args:
        img_eq: Input image to be equalized.

    Returns:
        Equalized image.
    """
    clahe = cv2.createCLAHE(clipLimit=10)
    return clahe.apply(img_eq)


def equalize(im_g: np.ndarray) -> np.ndarray:
    """
    Equalizes the image using CLAHE after adjusting background intensity.

    Args:
        im_g: Grayscale image.

    Returns:
        Equalized image.
    """
    img_pre, mask = change_background_intensity_to_mean(im_g)
    img_pre = equalize_image_using_clahe(img_pre)
    img_pre = change_background_to_value(img_pre, mask, Color.gray_white)
    return img_pre
