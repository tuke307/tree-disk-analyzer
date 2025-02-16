from typing import List, Tuple
import numpy as np
import cv2
import logging

from ..geometry.ray import Ray
from ..geometry.curve import Curve
from ..visualization.color import Color
from ..config import config

logger = logging.getLogger(__name__)


def calculate_average_ring_count(
    curves: List[Curve],
    img_in: np.ndarray,
    num_rays: int = 12,
) -> int:
    """
    Calculates the average number of curve intersections along `num_rays` rays
    emanating from the center of the pith.

    Args:
        curves (List[Curve]): List of Devernay Curve objects.
        center (Tuple[float, float]): Center of the pith (x, y).
        height (int): Image height.
        width (int): Image width.
        num_rays (int): Number of rays to sample (default is 8).

    Returns:
        float: Average number of intersections (ring count) along the rays.
    """
    center = (
        float(config.cx) if config.cx is not None else 0.0,
        float(config.cy) if config.cy is not None else 0.0,
    )
    height, width = img_in.shape[:2]

    # Build rays in evenly spaced directions (angles in degrees).
    # Note: Here we use a list comprehension similar to build_rays but override the number of rays.
    angles = np.linspace(0, 360, num_rays, endpoint=False)
    rays = [Ray(angle, center, height, width) for angle in angles]

    counts = []
    # For each ray, count how many curves it intersects.
    for ray in rays:
        count = 0
        for curve in curves:
            # Check if the ray intersects the curve.
            if ray.geometry.intersects(curve.geometry):
                # The intersection can be a Point, MultiPoint, or even a LineString.
                inter = ray.geometry.intersection(curve.geometry)
                # We count each curve only once per ray even if multiple intersection points exist.
                if not inter.is_empty:
                    count += 1
        counts.append(count)

    # Compute the average and round it to an integer (total number)
    average_count = int(round(np.mean(counts)))

    # Debug mode: Print information and draw the rays and center on an image.
    if config.debug:
        logger.debug(f"Average ring count: {average_count}")
        logger.debug(f"Center: {center}")
        for ray in rays:
            logger.debug(f"Ray: {ray}")

        # Use the original image as a base for the debug image.
        debug_img = img_in.copy()

        # Draw each ray as a white line.
        for ray in rays:
            x_coords, y_coords = ray.geometry.xy
            start_pt = (int(round(x_coords[0])), int(round(y_coords[0])))
            end_pt = (int(round(x_coords[1])), int(round(y_coords[1])))
            cv2.line(debug_img, start_pt, end_pt, Color.blue, 1)

        # Draw the center as a red circle.
        center_pt = (int(round(center[0])), int(round(center[1])))
        cv2.circle(debug_img, center_pt, 5, Color.red, -1)

        # Save the debug image.
        debug_filename = f"{config.output_dir}/debug_rays.png"
        cv2.imwrite(debug_filename, debug_img)
        logger.debug(f"Saved debug image to {debug_filename}")

    return average_count
