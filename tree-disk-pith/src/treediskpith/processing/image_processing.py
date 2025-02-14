import numpy as np
from PIL import Image
import cv2
from typing import Tuple, Optional, List


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
