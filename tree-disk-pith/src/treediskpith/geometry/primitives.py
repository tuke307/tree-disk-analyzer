from dataclasses import dataclass
from typing import Optional, Tuple, Union
import numpy as np


@dataclass
class Point:
    """Represents a 2D point in pixel coordinates."""

    x: float
    y: float

    def to_array(self) -> np.ndarray:
        """Convert point to numpy array."""
        return np.array([self.x, self.y])

    @classmethod
    def from_array(cls, arr: np.ndarray) -> "Point":
        """Create point from numpy array."""
        return cls(float(arr[0]), float(arr[1]))


class Line:
    """
    Represents a 2D line defined by two points or by the line equation ax + by + c = 0.
    """

    def __init__(
        self,
        p1: Optional[Union[Point, np.ndarray]] = None,
        p2: Optional[Union[Point, np.ndarray]] = None,
        p1_rel: Optional[Union[Point, np.ndarray]] = None,
        p2_rel: Optional[Union[Point, np.ndarray]] = None,
        certainty: float = 1.0,
        coefficients: Optional[Tuple[float, float, float]] = None,
    ) -> None:
        """
        Initialize a line with either two points or line coefficients.

        Args:
            p1: First absolute point
            p2: Second absolute point
            p1_rel: First point relative to block
            p2_rel: Second point relative to block
            certainty: Confidence in line detection (0-1)
            coefficients: Line equation coefficients (a, b, c)
        """
        from .geometry.geometry_utils import euclidean_distance

        # Convert numpy arrays to Points if necessary
        self.p1 = Point.from_array(p1) if isinstance(p1, np.ndarray) else p1
        self.p2 = Point.from_array(p2) if isinstance(p2, np.ndarray) else p2
        self.p1_rel = (
            Point.from_array(p1_rel) if isinstance(p1_rel, np.ndarray) else p1_rel
        )
        self.p2_rel = (
            Point.from_array(p2_rel) if isinstance(p2_rel, np.ndarray) else p2_rel
        )

        self.certainty = certainty
        self.block_pointer: Optional[int] = None

        # Store line equation coefficients
        if coefficients is not None:
            self.a, self.b, self.c = coefficients
        elif self.p1 is not None and self.p2 is not None:
            self.a, self.b, self.c = self._compute_coefficients(self.p1, self.p2)
        else:
            self.a = self.b = self.c = None

        # Calculate length if absolute points are available
        self.length = (
            euclidean_distance(self.p1.to_array(), self.p2.to_array())
            if self.p1 is not None and self.p2 is not None
            else None
        )

    @staticmethod
    def _compute_coefficients(p1: Point, p2: Point) -> Tuple[float, float, float]:
        """
        Compute line equation coefficients (ax + by + c = 0).

        Args:
            p1: First point
            p2: Second point

        Returns:
            Tuple of coefficients (a, b, c)
        """
        if np.isclose(p2.x, p1.x):
            # Vertical line: x = c
            return 1.0, 0.0, -p1.x
        elif np.isclose(p1.y, p2.y):
            # Horizontal line: y = c
            return 0.0, 1.0, -p1.y
        else:
            a = p1.y - p2.y
            b = p2.x - p1.x
            c = p2.x * p1.y - p1.x * p2.y
            return a, b, c

    @staticmethod
    def get_line_coordinates(
        a: float,
        b: float,
        c: float,
        x: Optional[float] = None,
        y: Optional[float] = None,
    ) -> Tuple[Optional[float], Optional[float]]:
        """
        Given a line defined by coefficients a, b, c, computes the missing coordinate x or y.

        Args:
            a: Coefficient 'a' in the line equation.
            b: Coefficient 'b' in the line equation.
            c: Coefficient 'c' in the line equation.
            x: x-coordinate (optional).
            y: y-coordinate (optional).

        Returns:
            A tuple (x, y) representing the coordinates on the line. Returns (None, None) if both x and y are None.
        """
        if x is None and y is None:
            return None, None

        if np.isclose(a, 0) and np.isclose(b, 0):
            return None, None

        if np.isclose(a, 0) and not np.isclose(b, 0):
            y = -c / b
            return x if x is not None else 0.0, y

        if np.isclose(b, 0) and not np.isclose(a, 0):
            x = -c / a
            return x, y if y is not None else 0.0

        if x is not None:
            y = (-a * x - c) / b
            return x, y

        if y is not None:
            x = (-b * y - c) / a
            return x, y

        return None, None
