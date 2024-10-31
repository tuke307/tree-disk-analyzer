import numpy as np
import cv2
from typing import List, Optional, Tuple


def from_lines_to_matrix(l_lo: List["Line"]) -> np.ndarray:
    """
    Converts a list of Line objects to a NumPy matrix of their endpoints.

    Args:
        l_lo: List of Line objects.

    Returns:
        A NumPy array of shape (n_lines, 4), where each row contains the endpoints
        [x1, y1, x2, y2] of a line.
    """
    L = np.zeros((len(l_lo), 4))
    for idx, li in enumerate(l_lo):
        x1, y1 = li.p1.ravel()
        x2, y2 = li.p2.ravel()
        L[idx] = [x1, y1, x2, y2]
    return L


def euclidean_distance(p1: np.ndarray, p2: np.ndarray) -> float:
    """
    Computes the Euclidean distance between two points.

    Args:
        p1: First point as a NumPy array.
        p2: Second point as a NumPy array.

    Returns:
        The Euclidean distance between p1 and p2.
    """
    return np.linalg.norm(p1 - p2)


class Line:
    def __init__(
        self,
        p1_rel: Optional[np.ndarray] = None,
        p2_rel: Optional[np.ndarray] = None,
        p1: Optional[np.ndarray] = None,
        p2: Optional[np.ndarray] = None,
        certainty: float = 1,
        a: Optional[float] = None,
        b: Optional[float] = None,
        c: Optional[float] = None,
    ):
        """
        Represents a line defined by two points or by the line equation a*x + b*y + c = 0.

        Args:
            p1_rel: Point 1 relative to the block (pixel coordinates).
            p2_rel: Point 2 relative to the block (pixel coordinates).
            p1: Point 1 absolute coordinates (pixel).
            p2: Point 2 absolute coordinates (pixel).
            certainty: Certainty of the line estimation.
            a: Coefficient 'a' in the line equation.
            b: Coefficient 'b' in the line equation.
            c: Coefficient 'c' in the line equation.
        """
        self.p1_rel = np.array(p1_rel) if p1_rel is not None else None
        self.p2_rel = np.array(p2_rel) if p2_rel is not None else None
        self.p1 = np.array(p1) if p1 is not None else None
        self.p2 = np.array(p2) if p2 is not None else None
        self.certainty = certainty
        self.block_pointer: Optional[int] = None
        self.a = a
        self.b = b
        self.c = c
        if self.p1 is not None and self.p2 is not None:
            self.length = euclidean_distance(self.p1, self.p2)
        else:
            self.length = None

    def get_slope_bias(self, H: int, W: int) -> Tuple[Optional[float], Optional[float]]:
        """
        Computes the slope and bias of the line in normalized coordinates.

        Args:
            H: Height of the image/block.
            W: Width of the image/block.

        Returns:
            A tuple (slope, bias). If the line is vertical, slope is None and bias is x-intercept.
            If the line is horizontal, slope is 0 and bias is y-intercept.
        """
        if self.p1 is None or self.p2 is None:
            return None, None
        y1, x1 = self.p1.ravel()
        y2, x2 = self.p2.ravel()

        # Normalize coordinates
        x1 /= W
        y1 /= H
        x2 /= W
        y2 /= H

        # Compute slope and bias
        if np.isclose(x2, x1):
            # Vertical line: x = c
            return None, x1
        elif np.isclose(y1, y2):
            # Horizontal line: y = c
            return 0.0, y1
        else:
            slope = (y2 - y1) / (x2 - x1)
            bias = y1 - slope * x1
            return slope, bias

    def set_block_pointer(self, idx: int) -> None:
        """
        Sets the block identifier to which the line belongs.

        Args:
            idx: Block identifier referring to the original block list.

        Returns:
            None
        """
        self.block_pointer = idx

    @staticmethod
    def compute_line_coefficients(
        p1: np.ndarray, p2: np.ndarray
    ) -> Tuple[float, float, float]:
        """
        Given two points, computes the coefficients (a, b, c) of the line equation a*x + b*y + c = 0.

        Args:
            p1: First point as a NumPy array.
            p2: Second point as a NumPy array.

        Returns:
            A tuple (a, b, c) representing the coefficients of the line.
        """
        x1, y1 = p1.ravel()
        x2, y2 = p2.ravel()

        if np.isclose(x2, x1):
            # Vertical line: x = c
            a = 1.0
            b = 0.0
            c = -x1
        elif np.isclose(y1, y2):
            # Horizontal line: y = c
            a = 0.0
            b = 1.0
            c = -y1
        else:
            a = y1 - y2
            b = x2 - x1
            c = x2 * y1 - x1 * y2

        return a, b, c

    def compute_intersection_with_line(
        self, line: "Line"
    ) -> Tuple[Optional[float], Optional[float]]:
        """
        Computes the intersection point between this line and another line.

        Args:
            line: Another Line object.

        Returns:
            A tuple (x, y) representing the intersection point. Returns (None, None) if no intersection.
        """
        a1, b1, c1 = self.compute_line_coefficients(self.p1, self.p2)
        a2, b2, c2 = line.compute_line_coefficients(line.p1, line.p2)
        determinant = a1 * b2 - a2 * b1

        if np.isclose(determinant, 0):
            # No intersection
            return None, None

        x = (b2 * c1 - b1 * c2) / determinant
        y = (a1 * c2 - a2 * c1) / determinant
        return x, y

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

    def compute_intersection_with_block_boundaries(
        self, p1: np.ndarray, p2: np.ndarray, img: np.ndarray
    ) -> Tuple[float, float, float, float, float, float, float, float]:
        """
        Computes the intersections of the line with the boundaries of the image/block.

        Args:
            p1: First point as a NumPy array.
            p2: Second point as a NumPy array.
            img: Image or block as a NumPy array.

        Returns:
            A tuple of eight floats representing the intersection points with the boundaries:
            (x1, y1, x2, y2, x3, y3, x4, y4)
        """
        # Get the image dimensions
        if img.ndim == 3:
            height, width, _ = img.shape
        else:
            height, width = img.shape

        if self.a is None or self.b is None or self.c is None:
            a, b, c = self.compute_line_coefficients(p1, p2)
        else:
            a, b, c = self.a, self.b, self.c

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
        x1, y1 = self.get_line_coordinates(a, b, c, x=x1)
        x2, y2 = self.get_line_coordinates(a, b, c, x=x2)
        x3, y3 = self.get_line_coordinates(a, b, c, y=y3)
        x4, y4 = self.get_line_coordinates(a, b, c, y=y4)

        return x1, y1, x2, y2, x3, y3, x4, y4

    @staticmethod
    def draw_line(
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        block: np.ndarray,
        thickness: int,
        color: Tuple[int, int, int],
    ) -> np.ndarray:
        """
        Draws a line on a given block/image.

        Args:
            x1: x-coordinate of the first point.
            y1: y-coordinate of the first point.
            x2: x-coordinate of the second point.
            y2: y-coordinate of the second point.
            block: Image or block as a NumPy array.
            thickness: Thickness of the line.
            color: Color of the line as a tuple (B, G, R).

        Returns:
            The block/image with the line drawn on it.
        """
        # Draw the line
        start_point = (int(round(x1)), int(round(y1)))
        end_point = (int(round(x2)), int(round(y2)))
        return cv2.line(block.copy(), start_point, end_point, color, thickness)

    def block_draw_line(
        self,
        block: np.ndarray,
        color: Tuple[int, int, int] = (0, 0, 255),
        thickness: int = 2,
        extended: bool = True,
    ) -> np.ndarray:
        """
        Draws the line on the given block.

        Args:
            block: Image or block as a NumPy array.
            color: Color of the line as a tuple (B, G, R).
            thickness: Thickness of the line.
            extended: If True, draws the line extended to the block boundaries.

        Returns:
            The block/image with the line drawn on it.
        """
        # Convert binary block array to RGB
        if len(block.shape) == 2:
            block = cv2.cvtColor(block.astype(np.uint8), cv2.COLOR_GRAY2RGB)

        if not extended:
            return block.copy()

        # Calculate the intersections with the image boundaries
        x1, y1, x2, y2, x3, y3, x4, y4 = (
            self.compute_intersection_with_block_boundaries(
                self.p1_rel, self.p2_rel, block
            )
        )
        # Choose two valid points to draw the line
        points = [
            (x1, y1),
            (x2, y2),
            (x3, y3),
            (x4, y4),
        ]
        valid_points = [(x, y) for x, y in points if x is not None and y is not None]
        if len(valid_points) >= 2:
            (x_start, y_start), (x_end, y_end) = valid_points[:2]
            extended_line = self.draw_line(
                x_start, y_start, x_end, y_end, block, thickness, color
            )
            return extended_line
        else:
            return block.copy()

    def img_draw_line(
        self,
        img: np.ndarray,
        color: Tuple[int, int, int] = (0, 0, 255),
        thickness: int = 2,
    ) -> np.ndarray:
        """
        Draws the extended line on the image.

        Args:
            img: Image as a NumPy array.
            color: Color of the line as a tuple (B, G, R).
            thickness: Thickness of the line.

        Returns:
            The image with the line drawn on it.
        """
        # Calculate the intersections with the image boundaries
        x1, y1, x2, y2, x3, y3, x4, y4 = (
            self.compute_intersection_with_block_boundaries(
                self.p1.ravel(), self.p2.ravel(), img
            )
        )
        # Choose two valid points to draw the line
        points = [
            (x1, y1),
            (x2, y2),
            (x3, y3),
            (x4, y4),
        ]
        valid_points = [(x, y) for x, y in points if x is not None and y is not None]
        if len(valid_points) >= 2:
            (x_start, y_start), (x_end, y_end) = valid_points[:2]
            extended_line = self.draw_line(
                x_start, y_start, x_end, y_end, img, thickness, color
            )
            return extended_line
        else:
            return img.copy()

    def img_draw_segment(
        self,
        img: np.ndarray,
        color: Tuple[int, int, int] = (0, 0, 255),
        thickness: int = 2,
    ) -> np.ndarray:
        """
        Draws the line segment (between p1 and p2) on the image.

        Args:
            img: Image as a NumPy array.
            color: Color of the line as a tuple (B, G, R).
            thickness: Thickness of the line.

        Returns:
            The image with the line segment drawn on it.
        """
        # Draw the line segment on the image
        extended_line = self.draw_line(
            self.p1[0], self.p1[1], self.p2[0], self.p2[1], img, thickness, color
        )
        return extended_line

    def distance_to_point(self, point: Tuple[float, float]) -> float:
        """
        Computes the minimum distance between the line and a point.

        Args:
            point: A tuple (x, y) representing the point.

        Returns:
            The minimum distance between the line and the point.
        """
        a, b, c = self.compute_line_coefficients(self.p1, self.p2)
        x, y = point
        denominator = np.sqrt(a**2 + b**2)
        if np.isclose(denominator, 0):
            return float("inf")
        return np.abs(a * x + b * y + c) / denominator
