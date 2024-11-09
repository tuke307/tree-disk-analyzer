from typing import Optional, Tuple
import numpy as np


class LeastSquaresSolution:
    """
    Solves the optimization problem using the Least Squares method to find the point
    minimizing the distances to a set of lines.
    """

    def __init__(
        self,
        line_segments: np.ndarray,
        output_dir: Optional[str] = None,
        img: Optional[np.ndarray] = None,
        debug: bool = False,
    ) -> None:
        """
        Initialize the solver with line segments and optional parameters.

        Args:
            line_segments: Array of line segments, shape (N, 4) where each row is [x1, y1, x2, y2]
            output_dir: Directory for output files (if any)
            img: Reference image array (optional)
            debug: Enable debug mode
        """
        self._validate_input(line_segments)
        self.lines = line_segments
        self.img = img
        self.output_dir = output_dir
        self.debug = debug
        self.num_lines = self.lines.shape[0]

    def _validate_input(self, line_segments: np.ndarray) -> None:
        """
        Validate the input line segments array.

        Args:
            line_segments: Input array to validate

        Raises:
            ValueError: If input array has incorrect shape or type
        """
        if not isinstance(line_segments, np.ndarray):
            raise ValueError("Line segments must be a numpy array")
        if len(line_segments.shape) != 2 or line_segments.shape[1] != 4:
            raise ValueError("Line segments must have shape (N, 4)")

    @staticmethod
    def compute_line_coefficients(
        p1: Tuple[float, float], p2: Tuple[float, float]
    ) -> Tuple[float, float, float]:
        """
        Compute coefficients (a, b, c) for the line equation ax + by + c = 0.

        Args:
            p1: First point [x1, y1]
            p2: Second point [x2, y2]

        Returns:
            Tuple of (a, b, c) coefficients
        """
        x1, y1 = p1
        x2, y2 = p2

        # Handle special cases
        if np.isclose(x2, x1):
            return 1.0, 0.0, -x1  # Vertical line
        if np.isclose(y1, y2):
            return 0.0, 1.0, -y1  # Horizontal line

        # General case
        a = y1 - y2
        b = x2 - x1
        c = x1 * y2 - x2 * y1

        return a, b, c

    def _build_equation_system(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Build the system of equations for least squares solution.

        Returns:
            Tuple of (B, g) where B is the coefficient matrix and g is the constant vector
        """
        B = np.zeros((self.num_lines, 2))
        g = np.zeros((self.num_lines, 1))

        for idx, line in enumerate(self.lines):
            x1, y1, x2, y2 = line
            a, b, c = self.compute_line_coefficients(
                np.array([x1, y1]), np.array([x2, y2])
            )
            # Normalize coefficients
            norm = np.sqrt(a**2 + b**2)
            norm = max(norm, 1e-8)  # Avoid division by zero

            B[idx] = np.array([a, b]) / norm
            g[idx] = -c / norm

        return B, g

    def _get_fallback_point(self) -> Tuple[float, float]:
        """
        Get fallback point (image center) when solution fails.

        Returns:
            Tuple of (x, y) coordinates of image center
        """
        if self.img is not None:
            h, w, _ = self.img.shape
            return w / 2, h / 2
        return 0.0, 0.0

    def run(self) -> Tuple[float, float]:
        """
        Find the point that minimizes the sum of squared distances to all lines.

        Returns:
            Tuple of (x, y) coordinates of the optimal point
        """
        # Build the equation system
        B, g = self._build_equation_system()

        # Solve using normal equations: (B^T B)x = B^T g
        BTB = B.T @ B
        try:
            solution = np.linalg.solve(BTB, B.T @ g)
            return float(solution[0, 0]), float(solution[1, 0])
        except np.linalg.LinAlgError:
            # Fallback to image center if solution doesn't exist
            return self._get_fallback_point()
