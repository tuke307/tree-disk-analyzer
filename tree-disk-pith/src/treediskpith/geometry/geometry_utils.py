import numpy as np


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
