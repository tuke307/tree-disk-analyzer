from typing import Any, List, Tuple

import numpy as np
from shapely.geometry import LineString


class Ray:
    def __init__(self, direction: float, center: Tuple[float, float], M: int, N: int):
        """
        Initializes a Ray object.

        Args:
            direction (float): Angle direction of the ray in degrees.
            center (Tuple[float, float]): Center coordinates (y, x).
            M (int): Height of the image.
            N (int): Width of the image.

        Returns:
            None
        """
        self.direction = direction
        self.center = center
        self.M = M
        self.N = N
        self.border = self._image_border_radii_intersection(direction, center, M, N)
        self.geometry = LineString([center, self.border])

    @staticmethod
    def _image_border_radii_intersection(
        theta: float, origin: Tuple[float, float], M: int, N: int
    ) -> Tuple[float, float]:
        """
        Computes the intersection point of a ray with the image border.

        Args:
            theta (float): Angle of the ray in degrees.
            origin (Tuple[float, float]): Origin point (y, x).
            M (int): Height of the image.
            N (int): Width of the image.

        Returns:
            Tuple[float, float]: Intersection point coordinates (y, x).
        """
        degree_to_radians = np.pi / 180
        theta = theta % 360
        yc, xc = origin
        if 0 <= theta < 45:
            ye = M - 1
            xe = np.tan(theta * degree_to_radians) * (M - 1 - yc) + xc
        elif 45 <= theta < 90:
            xe = N - 1
            ye = np.tan((90 - theta) * degree_to_radians) * (N - 1 - xc) + yc
        elif 90 <= theta < 135:
            xe = N - 1
            ye = yc - np.tan((theta - 90) * degree_to_radians) * (xe - xc)
        elif 135 <= theta < 180:
            ye = 0
            xe = np.tan((180 - theta) * degree_to_radians) * yc + xc
        elif 180 <= theta < 225:
            ye = 0
            xe = xc - np.tan((theta - 180) * degree_to_radians) * yc
        elif 225 <= theta < 270:
            xe = 0
            ye = yc - np.tan((270 - theta) * degree_to_radians) * xc
        elif 270 <= theta < 315:
            xe = 0
            ye = np.tan((theta - 270) * degree_to_radians) * xc + yc
        elif 315 <= theta < 360:
            ye = M - 1
            xe = xc - np.tan((360 - theta) * degree_to_radians) * (ye - yc)
        else:
            raise ValueError("Invalid theta value")
        return (ye, xe)
