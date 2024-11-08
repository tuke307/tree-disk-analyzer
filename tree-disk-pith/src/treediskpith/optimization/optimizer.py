import numpy as np
import cv2
from scipy.optimize import minimize
from typing import Optional, Tuple, Any

from ..processing.image_processing import resize_image_using_pil_lib
from ..visualization.color import Color


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
        line_segments: np.ndarray,
        output_dir: Optional[str] = None,
        img: Optional[np.ndarray] = None,
        weights: Optional[np.ndarray] = None,
        debug: bool = False,
        logger: Optional[Any] = None,
    ) -> None:
        """
        Initializes the Optimization class.

        Args:
            line_segments: Initial set of line segments as a NumPy array of shape (N, 4).
            output_dir: Directory path for output files.
            img: Image array.
            weights: Optional weights for the optimization.
            debug: Flag to enable debug mode.
            logger: Optional logger for logging messages.

        Returns:
            None
        """
        self.L_init = line_segments
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
                debug_img,
            )

        return x, y, value
