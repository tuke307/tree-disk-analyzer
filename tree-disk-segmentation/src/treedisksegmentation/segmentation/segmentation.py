import cv2
import numpy as np
from typing import Tuple
from PIL import Image


def polygon_to_mask(image: Image.Image, polygon_points: list) -> np.ndarray:
    """
    Converts a list of polygon points (from YOLO detections) into a binary mask.

    Args:
        image (Image.Image): The original PIL image.
        polygon_points (list): List of dictionaries with keys 'x' and 'y'.

    Returns:
        np.ndarray: Binary mask (uint8) with the polygon filled in white (255) and the rest black (0).
    """
    width, height = image.size  # PIL returns (width, height)
    mask = np.zeros((height, width), dtype=np.uint8)
    pts = np.array(
        [[int(pt["x"]), int(pt["y"])] for pt in polygon_points], dtype=np.int32
    )
    pts = pts.reshape((-1, 1, 2))
    cv2.fillPoly(mask, [pts], color=(255,))
    return mask


def apply_mask(image: Image.Image, mask: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Applies the provided binary mask to the image so that areas outside the polygon
    are set to white.

    Args:
        image (Image.Image): The original PIL image.
        mask (np.ndarray): A binary mask (with 0 for background and 255 for foreground).

    Returns:
        Tuple[np.ndarray, np.ndarray]:
            - The resulting image with the mask overlay applied (as a numpy array).
            - The mask itself as a uint8 numpy array.
    """
    # Convert the image to a numpy array.
    image_np = np.array(image)

    # Ensure the mask has a channel dimension.
    mask_expanded = np.expand_dims(mask, axis=2)

    # Apply the mask: multiply by the normalized mask (i.e. 0 or 1)
    masked_image = (image_np * (mask_expanded / 255)).astype(np.uint8)

    # Set background pixels (where mask==0) to white.
    background_mask = mask_expanded.squeeze() == 0
    masked_image[background_mask] = [255, 255, 255]

    return masked_image, mask
