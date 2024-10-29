import numpy as np
import cv2
from scipy.optimize import minimize
from typing import Optional, Tuple, Any

from lib.image import Drawing, Color, resize_image_using_pil_lib


class Optimization:
    """
    Implementation of the optimization of the convex function:

        1/N * sum_{i=1}^N f(x_i)

    where f(x_i) is the functional:

        cos^2(theta_i) = ((A ⋅ B) / (||A|| ||B||))^2

    The optimization is performed using gradient descent.
    """

    def __init__(
        self,
        m_lsd: np.ndarray,
        output_dir: Optional[str] = None,
        img: Optional[np.ndarray] = None,
        weights: Optional[np.ndarray] = None,
        debug: bool = False,
        logger: Optional[Any] = None,
    ) -> None:
        """
        Initializes the Optimization class.

        Args:
            m_lsd: Initial set of line segments as a NumPy array of shape (N, 4).
            output_dir: Directory path for output files.
            img: Image array.
            weights: Optional weights for the optimization.
            debug: Flag to enable debug mode.
            logger: Optional logger for logging messages.

        Returns:
            None
        """
        self.L_init = m_lsd
        self.img = img
        self.output_dir = output_dir
        self.debug = debug
        self.N = self.L_init.shape[0]
        self.weights_init = weights
        self.logger = logger

    @staticmethod
    def object_function(variables: np.ndarray, coefs: np.ndarray) -> float:
        """
        Objective function to be minimized.

        Args:
            variables: Variables to optimize, array of shape (2,), [x, y].
            coefs: Coefficients array from line segments of shape (N, 4).

        Returns:
            Negative of the mean squared cosine of angles between vectors.
        """
        X1, Y1, X2, Y2 = coefs[:, 0], coefs[:, 1], coefs[:, 2], coefs[:, 3]
        x, y = variables

        Xc = (X1 + X2) / 2
        Yc = (Y1 + Y2) / 2
        AA = np.vstack((X1 - X2, Y1 - Y2)).T
        BB = np.vstack((Xc - x, Yc - y)).T

        # Normalize vectors and handle zero norms to avoid division by zero
        AA_norm = np.linalg.norm(AA, axis=1).reshape(-1, 1)
        BB_norm = np.linalg.norm(BB, axis=1).reshape(-1, 1)
        AA_norm[AA_norm == 0] = 1e-8
        BB_norm[BB_norm == 0] = 1e-8

        AA_normalized = AA / AA_norm
        BB_normalized = BB / BB_norm

        value = np.sum(AA_normalized * BB_normalized, axis=1) ** 2
        res = value.mean()
        return -res

    def run(self, xo: float, yo: float) -> Tuple[float, float, float]:
        """
        Runs the optimization process to minimize the objective function.

        Args:
            xo: Initial x-coordinate guess.
            yo: Initial y-coordinate guess.

        Returns:
            A tuple containing the optimized x, y coordinates and the function value.
        """
        # Handle image dimensions
        H, W, _ = self.img.shape if self.img is not None else (0, 0, 0)

        if self.debug and self.img is not None:
            debug_img = self.img.copy()

        results = minimize(
            self.object_function, [xo, yo], args=(self.L_init,), tol=1e-6
        )

        x, y = results.x
        value = -results.fun

        if self.debug and self.img is not None:
            debug_img = cv2.circle(
                debug_img,
                (int(round(x)), int(round(y))),
                2,
                Color.red,
                -1,
            )
            cv2.imwrite(
                f"{self.output_dir}_op.png",
                resize_image_using_pil_lib(debug_img, 640, 640),
            )

        return x, y, value


class LeastSquaresSolution:
    """
    Solves the optimization problem using the Least Squares method to find the point minimizing
    the distances to a set of lines.
    """

    def __init__(
        self,
        m_lsd: np.ndarray,
        output_dir: Optional[str] = None,
        img: Optional[np.ndarray] = None,
        debug: bool = False,
    ) -> None:
        """
        Initializes the LeastSquaresSolution class.

        Args:
            m_lsd: Initial set of line segments as a NumPy array of shape (N, 4).
            output_dir: Directory path for output files.
            img: Image array.
            debug: Flag to enable debug mode.

        Returns:
            None
        """
        self.L_init = m_lsd
        self.img = img
        self.output_dir = output_dir
        self.debug = debug
        self.N = self.L_init.shape[0]

    @staticmethod
    def compute_line_coefficients(
        p1: np.ndarray, p2: np.ndarray
    ) -> Tuple[float, float, float]:
        """
        Given two points, compute the coefficients of the line equation a*x + b*y + c = 0.

        Args:
            p1: First point as a NumPy array [x1, y1].
            p2: Second point as a NumPy array [x2, y2].

        Returns:
            A tuple (a, b, c) representing the line coefficients.
        """
        x1, y1 = p1
        x2, y2 = p2

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
            c = x1 * y2 - x2 * y1

        return a, b, c

    def run(self) -> Tuple[float, float]:
        """
        Solves the Least Squares problem to find the point minimizing the distances to the lines.

        Returns:
            A tuple (x, y) representing the coordinates of the solution point.
        """
        H, W, _ = self.img.shape if self.img is not None else (0, 0, 0)

        # Compute coefficients
        num_lines = len(self.L_init)
        B = np.zeros((num_lines, 2))
        g = np.zeros((num_lines, 1))
        for idx, l in enumerate(self.L_init):
            x1, y1, x2, y2 = l
            a, b, c = self.compute_line_coefficients(
                np.array([x1, y1]), np.array([x2, y2])
            )
            denom = np.sqrt(a**2 + b**2)
            if np.isclose(denom, 0):
                denom = 1e-8  # Avoid division by zero
            B[idx] = np.array([a, b]) / denom
            g[idx] = -c / denom

        # Least Squares solution: B * [x, y] = g
        BTB = B.T @ B
        try:
            invBTB = np.linalg.inv(BTB)
        except np.linalg.LinAlgError as err:
            if "Singular matrix" in str(err):
                h, w, _ = self.img.shape if self.img is not None else (0, 0, 0)
                return w / 2, h / 2
            else:
                raise err

        x, y = invBTB @ B.T @ g
        return x[0], y[0]


def filter_lo_around_c(
    Lof: np.ndarray, rf: float, ci: Tuple[float, float], img_in: np.ndarray
) -> Tuple[np.ndarray, Tuple[float, float], Tuple[float, float]]:
    """
    Filters lines around a central point within a region defined by a reduction factor.

    Args:
        Lof: Array of line segments of shape (N, 4).
        rf: Reduction factor to define the region size.
        ci: Central point coordinates (x, y).
        img_in: Input image array.

    Returns:
        A tuple containing:
            - m_lines_within_region: Array of lines within the defined region.
            - top_left: Coordinates of the top-left corner of the region.
            - bottom_right: Coordinates of the bottom-right corner of the region.
    """
    x, y = ci
    H, W = img_in.shape[:2]
    # Define region
    top_left = (x - W / rf, y - H / rf)
    bottom_right = (x + W / rf, y + H / rf)

    m_lines_within_region, _ = get_lines_idx_within_rectangular_region(
        img_in,
        Lof,
        None,
        int(top_left[0]),
        int(top_left[1]),
        int(bottom_right[0]),
        int(bottom_right[1]),
        debug=False,
        output_path=None,
    )
    return m_lines_within_region, top_left, bottom_right


def get_lines_idx_within_rectangular_region(
    img_in: np.ndarray,
    L: np.ndarray,
    weights: Optional[np.ndarray],
    top_x: int,
    top_y: int,
    bottom_x: int,
    bottom_y: int,
    debug: bool,
    output_path: Optional[str] = None,
) -> Tuple[np.ndarray, Optional[np.ndarray]]:
    """
    Gets indices of lines within a rectangular region.

    Args:
        img_in: Input image array.
        L: Array of line segments of shape (N, 4).
        weights: Optional array of weights corresponding to the lines.
        top_x: Top-left x-coordinate of the region.
        top_y: Top-left y-coordinate of the region.
        bottom_x: Bottom-right x-coordinate of the region.
        bottom_y: Bottom-right y-coordinate of the region.
        debug: Flag to enable debug mode.
        output_path: Optional path to save debug images.

    Returns:
        A tuple containing:
            - l_lines_within_region: Array of lines within the region.
            - weights_within_region: Weights corresponding to the lines within the region.
    """
    X1, Y1, X2, Y2 = L[:, 0], L[:, 1], L[:, 2], L[:, 3]

    X_min = np.minimum(X1, X2)
    X_max = np.maximum(X1, X2)
    Y_min = np.minimum(Y1, Y2)
    Y_max = np.maximum(Y1, Y2)

    idx = np.where(
        (top_x <= X_min) & (X_max <= bottom_x) & (top_y <= Y_min) & (Y_max <= bottom_y)
    )[0]
    l_lines_within_region = L[idx]
    weights_within_region = weights[idx] if weights is not None else None

    if debug:
        # Draw rectangular region
        img = img_in.copy()
        img = cv2.rectangle(img, (top_x, top_y), (bottom_x, bottom_y), Color.black, 2)
        Drawing.draw_lsd_lines(
            l_lines_within_region, img, output_path=output_path, lines_all=L
        )

    return l_lines_within_region, weights_within_region
