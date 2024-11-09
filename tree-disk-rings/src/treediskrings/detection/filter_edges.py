from typing import List, Optional

import cv2
import numpy as np

from ..visualization.color import Color
from ..geometry.curve import Curve
from ..config import config

DELIMITE_CURVE_ROW = np.array([-1, -1])


def normalized_row_matrix(matrix: np.ndarray) -> np.ndarray:
    """
    Normalizes each row of a matrix.

    Args:
        matrix (np.ndarray): Input matrix.

    Returns:
        np.ndarray: Matrix with rows normalized.
    """
    epsilon = 1e-10  # Small value to avoid division by zero
    sqrt = np.sqrt((matrix**2).sum(axis=1)) + epsilon
    normalized_array = matrix / sqrt[:, np.newaxis]
    return normalized_array


def erosion(erosion_size: int, src: np.ndarray) -> np.ndarray:
    """
    Applies erosion to an image.

    Args:
        erosion_size (int): Size of the erosion kernel.
        src (np.ndarray): Source image.

    Returns:
        np.ndarray: Eroded image.
    """
    erosion_shape = cv2.MORPH_CROSS
    element = cv2.getStructuringElement(
        erosion_shape,
        (2 * erosion_size + 1, 2 * erosion_size + 1),
        (erosion_size, erosion_size),
    )
    erosion_dst = cv2.erode(src, element)

    return erosion_dst


def dilatation(dilatation_size: int, src: np.ndarray) -> np.ndarray:
    """
    Applies dilation to an image.

    Args:
        dilatation_size (int): Size of the dilation kernel.
        src (np.ndarray): Source image.

    Returns:
        np.ndarray: Dilated image.
    """
    dilation_shape = cv2.MORPH_RECT
    element = cv2.getStructuringElement(
        dilation_shape,
        (2 * dilatation_size + 1, 2 * dilatation_size + 1),
        (dilatation_size, dilatation_size),
    )
    dilatation_dst = cv2.dilate(src, element)

    return dilatation_dst


def mask_background(img: np.ndarray) -> np.ndarray:
    """
    Creates a mask for the background of the image.

    Args:
        img (np.ndarray): Input image.

    Returns:
        np.ndarray: Mask of the background.
    """
    mask = np.zeros((img.shape[0], img.shape[1]), dtype=np.uint8)
    mask[img[:, :] == Color.gray_white] = Color.gray_white

    return mask


def blur(img: np.ndarray, blur_size: int = 11) -> np.ndarray:
    """
    Applies Gaussian blur to an image.

    Args:
        img (np.ndarray): Input image.
        blur_size (int): Size of the Gaussian kernel.

    Returns:
        np.ndarray: Blurred image.
    """
    return cv2.GaussianBlur(img, (blur_size, blur_size), 0)


def thresholding(mask: np.ndarray, threshold: int = 0) -> np.ndarray:
    """
    Applies thresholding to a mask.

    Args:
        mask (np.ndarray): Input mask.
        threshold (int): Threshold value.

    Returns:
        np.ndarray: Thresholded mask.
    """
    mask = np.where(mask > threshold, Color.gray_white, 0).astype(np.uint8)

    return mask


def padding_mask(mask: np.ndarray, pad: int = 3) -> np.ndarray:
    """
    Pads the mask with a constant value.

    Args:
        mask (np.ndarray): Input mask.
        pad (int): Padding size.

    Returns:
        np.ndarray: Padded mask.
    """
    mask = np.pad(
        mask, ((pad, pad), (pad, pad)), mode="constant", constant_values=255
    ).astype(np.uint8)
    return mask


def find_border_contour(mask: np.ndarray, img: np.ndarray) -> Optional[np.ndarray]:
    """
    Finds the contour of the border of the disk.

    Args:
        mask (np.ndarray): Background mask.
        img (np.ndarray): Disk image.

    Returns:
        Optional[np.ndarray]: Border contour coordinates, or None if not found.
    """
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    # 1.0 Perimeter of the image. Used to discard contours similar in size to the image perimeter.
    perimeter_image = 2 * img.shape[0] + 2 * img.shape[1]
    # 1.1 Error threshold. Discard contours similar in size to the image perimeter (within 10%).
    error_threshold = 0.1 * perimeter_image

    # 2.0 Approximate area of the wood cross-section disk.
    area_image = img.shape[0] * img.shape[1]
    approximate_disk_area = area_image / 2

    # 3.0 Find the contour closest in area to the approximate disk area.
    max_cont = None
    area_difference_min = np.inf
    for c in contours:
        contour_area = cv2.contourArea(c)
        contour_perimeter = cv2.arcLength(c, True)
        if np.abs(contour_perimeter - perimeter_image) < error_threshold:
            # Contour similar to image perimeter. Discard it.
            continue

        area_difference = np.abs(contour_area - approximate_disk_area)
        if area_difference < area_difference_min:
            max_cont = c.reshape((-1, 2))
            area_difference_min = area_difference

    return max_cont


def contour_to_curve(contour: np.ndarray, name: int) -> Curve:
    """
    Converts a contour to a Curve object.

    Args:
        contour (np.ndarray): Contour points.
        name (int): Identifier for the curve.

    Returns:
        Curve: Curve object created from the contour.
    """
    curve = Curve(contour.tolist(), name)

    return curve


def get_border_curve(img: np.ndarray, l_ch_f: List[Curve]) -> Curve:
    """
    Gets the border curve of the disk image. Implements Algorithm 5 in the supplementary material.

    Args:
        img (np.ndarray): Segmented grayscale image.
        l_ch_f (List[Curve]): List of curves.

    Returns:
        Curve: Border curve object.

    Raises:
        ValueError: If border contour cannot be found.
    """
    mask = mask_background(img)
    mask = blur(mask)
    mask = thresholding(mask)
    mask = padding_mask(mask)
    border_contour = find_border_contour(mask, img)

    if border_contour is None:
        raise ValueError("Border contour could not be found.")

    border_curve = contour_to_curve(border_contour, len(l_ch_f))

    return border_curve


def change_reference_axis(ch_e_matrix: np.array) -> np.array:
    """
    Changes the reference axis of the edge matrix to the center (cx, cy).

    Args:
        ch_e_matrix (np.array): Edge matrix.

    Returns:
        np.array: Transformed edge matrix.
    """
    center = [config.cx, config.cy]
    curve_border_index = np.where(ch_e_matrix == DELIMITE_CURVE_ROW)[0]
    X = ch_e_matrix.copy()

    # Change reference axis
    Xb = np.array([[1, 0], [0, 1]]).dot(X.T) + (
        np.array([-1, -1]) * np.array(center, dtype=float)
    ).reshape((-1, 1))

    # Mask delimiting edge row by -1
    Xb[:, curve_border_index] = -1

    return Xb


def convert_masked_pixels_to_curves(
    X_edges_filtered: np.ndarray,
) -> List[Curve]:
    """
    Converts masked pixels into Curve objects.

    Args:
        X_edges_filtered (np.ndarray): Filtered edge matrix.

    Returns:
        List[Curve]: List of Curve objects.
    """
    curve_border_index = np.unique(np.where(X_edges_filtered == DELIMITE_CURVE_ROW)[0])
    start = -1
    ch_f = []

    for end in curve_border_index:
        if end - start > 2:
            pixel_list = X_edges_filtered[start + 1 : end].tolist()
            curve = Curve(pixel_list, len(ch_f))
            ch_f.append(curve)
        start = end

    return ch_f


def get_gradient_vector_for_each_edge_pixel(
    ch_e: np.ndarray, Gx: np.ndarray, Gy: np.ndarray
) -> np.ndarray:
    """
    Gets the gradient vector for each edge pixel.

    Args:
        ch_e (np.ndarray): Edge matrix.
        Gx (np.ndarray): Gradient image in x direction.
        Gy (np.ndarray): Gradient image in y direction.

    Returns:
        np.ndarray: Gradient vectors.
    """
    G = np.vstack(
        (
            Gx[ch_e[:, 1].astype(int), ch_e[:, 0].astype(int)],
            Gy[ch_e[:, 1].astype(int), ch_e[:, 0].astype(int)],
        )
    ).T

    return G


def compute_angle_between_gradient_and_edges(
    Xb_normed: np.ndarray, gradient_normed: np.ndarray
) -> np.ndarray:
    """
    Computes the angle between the gradient and the edges.

    Args:
        Xb_normed (np.ndarray): Normalized edge vectors.
        gradient_normed (np.ndarray): Normalized gradient vectors.

    Returns:
        np.ndarray: Angles in degrees.
    """
    theta = (
        np.arccos(np.clip((gradient_normed * Xb_normed).sum(axis=1), -1.0, 1.0))
        * 180
        / np.pi
    )

    return theta


def filter_edges_by_threshold(m_ch_e: np.ndarray, theta: np.ndarray) -> np.ndarray:
    """
    Filters edges by a threshold angle.

    Args:
        m_ch_e (np.ndarray): Edge matrix.
        theta (np.ndarray): Angles between gradient and edges.
        alpha (float): Threshold angle.

    Returns:
        np.ndarray: Filtered edge matrix.
    """
    X_edges_filtered = m_ch_e.copy()
    X_edges_filtered[theta >= config.alpha] = -1

    return X_edges_filtered


def filter_edges(
    devernay_edges: np.array,
    gradient_x_img: np.ndarray,
    gradient_y_img: np.ndarray,
    img_pre: np.ndarray,
) -> List[Curve]:
    """
    Filters edges to keep only the ones forming rings (early wood edges).

    Edge detector finds three types of edges: early wood transitions, latewood transitions, and radial edges produced by
    cracks and fungi. Only early wood edges form the rings. To filter out the others, the collinearity with the ray direction
    is computed and filtered depending on threshold (alpha). Implements Algorithm 4 in the supplementary material.

    Args:
        devernay_edges (np.array): Devernay curves in matrix format.
        gradient_x_img (np.ndarray): Gradient image in x direction.
        gradient_y_img (np.ndarray): Gradient image in y direction.
        img_pre (np.ndarray): Input image.

    Returns:
        List[Curve]: Filtered Devernay curves.
    """
    # Change reference axis
    Xb = change_reference_axis(devernay_edges)

    # Get normalized gradient at each edge
    G = get_gradient_vector_for_each_edge_pixel(
        devernay_edges, gradient_x_img, gradient_y_img
    )

    # Normalize gradient and rays
    Xb_normalized = normalized_row_matrix(Xb.T)
    G_normalized = normalized_row_matrix(G)

    # Compute angle between gradient and edges
    theta = compute_angle_between_gradient_and_edges(Xb_normalized, G_normalized)

    # Filter pixels by threshold
    X_edges_filtered = filter_edges_by_threshold(devernay_edges, theta)

    # Convert masked pixels to Curve objects
    l_ch_f = convert_masked_pixels_to_curves(X_edges_filtered)

    # Add border curve
    border_curve = get_border_curve(img_pre, l_ch_f)

    # Append border curve to the list
    l_ch_f.append(border_curve)

    return l_ch_f
