import cv2
from PIL import Image
import numpy as np
from typing import Tuple
import logging

from ..config import config

logger = logging.getLogger(__name__)

WHITE = 255
NONE = 0


def get_image_shape(img_in: np.ndarray) -> Tuple[int, int]:
    """
    Get image shape.

    Args:
        img_in (np.ndarray): Input image.

    Returns:
        Tuple[int, int]: Image height, image width.
    """
    if img_in.ndim > 2:
        height, width, _ = img_in.shape
    else:
        height, width = img_in.shape

    return height, width


def resize(img_in: cv2.typing.MatLike) -> Tuple[np.array, int, int]:
    """
    Resize image and keep the center of the image in the same position. Implements Algorithm 2 in the supplementary material.

    Args:
        img_in (cv2.typing.MatLike): Image to resize.

    Returns:
        Tuple[np.array, int, int]: Resized image, resized y's center coordinate, resized x's center coordinate.
    """
    logger.debug("Resizing image")

    current_height, current_width = get_image_shape(img_in)

    logger.debug(f"Current image shape: {current_height}x{current_width}")

    # Calculate missing dimension if needed
    if config.output_height is not None and config.output_width is None:
        aspect_ratio = current_width / current_height
        width_output = int(config.output_height * aspect_ratio)
        config.update(output_width=width_output)
    elif config.output_width is not None and config.output_height is None:
        aspect_ratio = current_height / current_width
        height_output = int(config.output_width * aspect_ratio)
        config.update(output_height=height_output)

    logger.debug(f"Resizing image to {config.output_height}x{config.output_width}")

    img_resized = resize_image_using_pil_lib(
        img_in, config.output_width, config.output_height
    )
    convert_center_coordinate_to_output_coordinate(current_height, current_width)

    return img_resized


def resize_image_using_pil_lib(
    img_in: cv2.typing.MatLike, target_width, target_height
) -> np.array:
    """
    Resize image using PIL library.

    Args:
        img_in (cv2.typing.MatLike): Input image.

    Returns:
        np.array: Matrix with the resized image.
    """
    image_pil = Image.fromarray(img_in)
    image_pil = image_pil.resize(
        (target_width, target_height), Image.Resampling.LANCZOS
    )
    # Convert PIL image to numpy array
    image_pil_resized = np.array(image_pil)

    return image_pil_resized


def convert_center_coordinate_to_output_coordinate(
    input_height: int, input_width: int
) -> None:
    """
    Convert center coordinate from input image to output image.

    Args:
        input_height (int): Input image height.
        input_width (int): Input image width.

    Returns:
        None
    """
    hscale = config.output_height / input_height
    wscale = config.output_width / input_width

    cy_output = config.cy * hscale
    cx_output = config.cx * wscale

    config.update(cy=cy_output, cx=cx_output)


def change_background_intensity_to_mean(
    img_in: np.ndarray,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Change background intensity to mean intensity.

    Args:
        img_in (np.ndarray): Input gray scale image. Background is white (255).

    Returns:
        Tuple[np.ndarray, np.ndarray]: Image with changed background intensity, background mask.
    """
    im_eq = img_in.copy()
    mask = np.where(img_in == 255, 1, 0)
    im_eq = change_background_to_value(im_eq, mask, np.mean(img_in[mask == 0]))

    return im_eq, mask


def equalize_image_using_clahe(img_eq: np.ndarray) -> np.ndarray:
    """
    Equalize image using CLAHE algorithm.

    Args:
        img_eq (np.ndarray): Image.

    Returns:
        np.ndarray: Equalized image.
    """
    clahe = cv2.createCLAHE(clipLimit=10)
    img_eq = clahe.apply(img_eq)

    return img_eq


def equalize(im_g: np.ndarray) -> np.ndarray:
    """
    Equalize image using CLAHE algorithm. Implements Algorithm 3 in the supplementary material.

    Args:
        im_gray (np.ndarray): Gray scale image.

    Returns:
        np.ndarray: Equalized image.
    """
    img_pre, mask = change_background_intensity_to_mean(im_g)
    img_pre = equalize_image_using_clahe(img_pre)
    img_pre = change_background_to_value(img_pre, mask, WHITE)

    return img_pre


def change_background_to_value(
    img_in: np.ndarray, mask: np.ndarray, value: int = 255
) -> np.ndarray:
    """
    Change background intensity to white.

    Args:
        img_in (np.ndarray): Input image.
        mask (np.ndarray): Background mask.
        value (int): Value to change the background to.

    Returns:
        np.ndarray: Image with changed background intensity.
    """
    img_in[mask > 0] = value

    return img_in


def rgb2gray(img_r: np.ndarray) -> np.ndarray:
    """
    Convert RGB image to grayscale.

    Args:
        img_r (np.ndarray): RGB image.

    Returns:
        np.ndarray: Grayscale image.
    """
    return cv2.cvtColor(img_r, cv2.COLOR_BGR2GRAY)


def preprocessing(img_in: cv2.typing.MatLike) -> Tuple[np.ndarray, int, int]:
    """
    Image preprocessing steps. Following actions are made:
    - Image resize
    - Image is converted to gray scale
    - Gray scale image is equalized
    Implements Algorithm 1 in the supplementary material.

    Args:
        img_in (cv2.typing.MatLike): Segmented image.

    Returns:
        Tuple[np.ndarray, int, int]: Equalized image, pith y's coordinate after resize, pith x's coordinate after resize.
    """
    if config.output_height is None and config.output_width is None:
        img_resized = img_in
    else:
        img_resized = resize(img_in)

    im_gray = rgb2gray(img_resized)
    img_pre = equalize(im_gray)

    return img_pre
