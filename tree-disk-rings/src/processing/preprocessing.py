import cv2
from PIL import Image
import numpy as np
from typing import Tuple


WHITE = 255
NONE = 0


def get_image_shape(im_in: np.ndarray) -> Tuple[int, int]:
    """
    Get image shape.

    Args:
        im_in (np.ndarray): Input image.

    Returns:
        Tuple[int, int]: Image height, image width.
    """
    if im_in.ndim > 2:
        height, width, _ = im_in.shape
    else:
        height, width = im_in.shape

    return height, width


def resize(
    im_in: np.ndarray,
    height_output: int,
    width_output: int,
    cy: int = 1,
    cx: int = 1,
) -> Tuple[np.ndarray, int, int]:
    """
    Resize image and keep the center of the image in the same position. Implements Algorithm 2 in the supplementary material.

    Args:
        im_in (np.ndarray): Gray image to resize.
        height_output (int): Output image height. If None, the image is not resized.
        width_output (int): Output image width. If None, the image is not resized.
        cy (int): Y's center coordinate in pixel.
        cx (int): X's center coordinate in pixel.

    Returns:
        Tuple[np.ndarray, int, int]: Resized image, resized y's center coordinate, resized x's center coordinate.
    """
    img_r = resize_image_using_pil_lib(im_in, height_output, width_output)
    height, width = get_image_shape(im_in)
    cy_output, cx_output = convert_center_coordinate_to_output_coordinate(
        cy, cx, height, width, height_output, width_output
    )

    return img_r, cy_output, cx_output


def resize_image_using_pil_lib(
    im_in: np.ndarray, height_output: int, width_output: int
) -> np.ndarray:
    """
    Resize image using PIL library.

    Args:
        im_in (np.ndarray): Input image.
        height_output (int): Output image height.
        width_output (int): Output image width.

    Returns:
        np.ndarray: Matrix with the resized image.
    """
    pil_img = Image.fromarray(im_in)
    flag = Image.Resampling.LANCZOS
    pil_img = pil_img.resize((height_output, width_output), flag)
    im_r = np.ndarray(pil_img)

    return im_r


def convert_center_coordinate_to_output_coordinate(
    cy: int, cx: int, height: int, width: int, height_output: int, width_output: int
) -> Tuple[int, int]:
    """
    Convert center coordinate from input image to output image.

    Args:
        cy (int): Y's center coordinate in pixel.
        cx (int): X's center coordinate in pixel.
        height (int): Input image height.
        width (int): Input image width.
        height_output (int): Output image height.
        width_output (int): Output image width.

    Returns:
        Tuple[int, int]: Resized y's center coordinate, resized x's center coordinate.
    """
    hscale = height_output / height
    wscale = width_output / width

    cy_output = cy * hscale
    cx_output = cx * wscale

    return cy_output, cx_output


def change_background_intensity_to_mean(
    im_in: np.ndarray,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Change background intensity to mean intensity.

    Args:
        im_in (np.ndarray): Input gray scale image. Background is white (255).

    Returns:
        Tuple[np.ndarray, np.ndarray]: Image with changed background intensity, background mask.
    """
    im_eq = im_in.copy()
    mask = np.where(im_in == 255, 1, 0)
    im_eq = change_background_to_value(im_eq, mask, np.mean(im_in[mask == 0]))

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
        im_g (np.ndarray): Gray scale image.

    Returns:
        np.ndarray: Equalized image.
    """
    im_pre, mask = change_background_intensity_to_mean(im_g)
    im_pre = equalize_image_using_clahe(im_pre)
    im_pre = change_background_to_value(im_pre, mask, WHITE)

    return im_pre


def change_background_to_value(
    im_in: np.ndarray, mask: np.ndarray, value: int = 255
) -> np.ndarray:
    """
    Change background intensity to white.

    Args:
        im_in (np.ndarray): Input image.
        mask (np.ndarray): Background mask.
        value (int): Value to change the background to.

    Returns:
        np.ndarray: Image with changed background intensity.
    """
    im_in[mask > 0] = value

    return im_in


def rgb2gray(img_r: np.ndarray) -> np.ndarray:
    """
    Convert RGB image to grayscale.

    Args:
        img_r (np.ndarray): RGB image.

    Returns:
        np.ndarray: Grayscale image.
    """
    return cv2.cvtColor(img_r, cv2.COLOR_BGR2GRAY)


def preprocessing(
    im_in: np.ndarray,
    height_output: int = None,
    width_output: int = None,
    cy: int = None,
    cx: int = None,
) -> Tuple[np.ndarray, int, int]:
    """
    Image preprocessing steps. Following actions are made:
    - Image resize
    - Image is converted to gray scale
    - Gray scale image is equalized
    Implements Algorithm 1 in the supplementary material.

    Args:
        im_in (np.ndarray): Segmented image.
        height_output (int): New image height.
        width_output (int): New image width.
        cy (int): Pith y's coordinate.
        cx (int): Pith x's coordinate.

    Returns:
        Tuple[np.ndarray, int, int]: Equalized image, pith y's coordinate after resize, pith x's coordinate after resize.
    """
    if NONE in [height_output, width_output]:
        im_r, cy_output, cx_output = (im_in, cy, cx)
    else:
        im_r, cy_output, cx_output = resize(im_in, height_output, width_output, cy, cx)

    im_g = rgb2gray(im_r)
    im_pre = equalize(im_g)

    return im_pre, cy_output, cx_output
