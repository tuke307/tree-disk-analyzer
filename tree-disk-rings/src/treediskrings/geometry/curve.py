from typing import List, Tuple
import numpy as np
import cv2
from shapely.geometry import LineString
from ..visualization.color import Color


class Curve:
    def __init__(self, pixels_list: List[Tuple[int, int]], name: int):
        """
        Initializes a Curve object.

        Args:
            pixels_list (List[Tuple[int, int]]): List of pixel coordinates (y, x).
            name (int): Identifier of the curve.
        """
        self.id = name
        self.geometry = LineString(np.array(pixels_list)[:, [1, 0]].tolist())

    def draw(self, img: np.ndarray, thickness: int = 1) -> np.ndarray:
        """
        Draws the curve on an image.

        Args:
            img (np.ndarray): Image on which to draw.
            thickness (int): Thickness of the curve lines.

        Returns:
            np.ndarray: Image with the curve drawn.
        """
        y, x = self.geometry.xy
        y = np.array(y).astype(int)
        x = np.array(x).astype(int)
        pts = np.vstack((x, y)).T
        isClosed = False
        img = cv2.polylines(img, [pts], isClosed, Color.black, thickness)

        return img
