import numpy as np
import cv2
from typing import Tuple, Optional, List

from ..visualization.color import Color
from ..processing.image_processing import (
    resize_image_using_pil_lib,
    compute_intersection_with_block_boundaries,
)


class Shapes:
    @staticmethod
    def rectangle(
        image: np.ndarray,
        top_left_point: Tuple[int, int],
        bottom_right_point: Tuple[int, int],
        color: Tuple[int, int, int] = Color.black,
        thickness: int = 2,
    ) -> np.ndarray:
        """
        Draws a rectangle on the image.

        Args:
            image: The input image.
            top_left_point: Coordinates of the top-left corner (x1, y1).
            bottom_right_point: Coordinates of the bottom-right corner (x2, y2).
            color: Color of the rectangle in BGR format.
            thickness: Thickness of the rectangle border. Use -1 for filled rectangle.

        Returns:
            The image with the rectangle drawn.
        """
        return cv2.rectangle(
            image.copy(), top_left_point, bottom_right_point, color, thickness
        )

    @staticmethod
    def circle(
        image: np.ndarray,
        center_coordinates: Tuple[int, int],
        thickness: int = -1,
        color: Tuple[int, int, int] = Color.black,
        radius: int = 3,
    ) -> np.ndarray:
        """
        Draws a circle on the image.

        Args:
            image: The input image.
            center_coordinates: Coordinates of the circle center (x, y).
            thickness: Thickness of the circle border. Use -1 for filled circle.
            color: Color of the circle in BGR format.
            radius: Radius of the circle.

        Returns:
            The image with the circle drawn.
        """
        return cv2.circle(image.copy(), center_coordinates, radius, color, thickness)

    @staticmethod
    def curve(
        curve_obj,
        img: np.ndarray,
        color: Tuple[int, int, int] = (0, 255, 0),
        thickness: int = 1,
    ) -> np.ndarray:
        """
        Draws a curve on the image.

        Args:
            curve_obj: An object with attributes 'xy' containing the coordinates of the curve.
            img: The input image.
            color: Color of the curve in BGR format.
            thickness: Thickness of the curve lines.

        Returns:
            The image with the curve drawn.
        """
        y, x = curve_obj.xy
        y = np.array(y).astype(int)
        x = np.array(x).astype(int)
        pts = np.vstack((x, y)).T.reshape(-1, 1, 2)
        is_closed = False

        return cv2.polylines(img.copy(), [pts], is_closed, color, thickness)

    @staticmethod
    def chain(
        chain_obj,
        img: np.ndarray,
        color: Tuple[int, int, int] = (0, 255, 0),
        thickness: int = 5,
    ) -> np.ndarray:
        """
        Draws a chain (sequence of points) on the image.

        Args:
            chain_obj: An object with method 'get_nodes_coordinates' returning coordinates.
            img: The input image.
            color: Color of the chain in BGR format.
            thickness: Thickness of the chain lines.

        Returns:
            The image with the chain drawn.
        """
        y, x = chain_obj.get_nodes_coordinates()
        pts = np.vstack((y, x)).T.astype(int).reshape(-1, 1, 2)
        is_closed = False

        return cv2.polylines(img.copy(), [pts], is_closed, color, thickness)

    @staticmethod
    def radii(
        rayo_obj,
        img: np.ndarray,
        color: Tuple[int, int, int] = (255, 0, 0),
        thickness: int = 1,
    ) -> np.ndarray:
        """
        Draws radii (lines) on the image.

        Args:
            rayo_obj: An object with attributes 'xy' containing the coordinates of the radii.
            img: The input image.
            color: Color of the radii in BGR format.
            thickness: Thickness of the radii lines.

        Returns:
            The image with the radii drawn.
        """
        y, x = rayo_obj.xy
        y = np.array(y).astype(int)
        x = np.array(x).astype(int)
        start_point = (x[0], y[0])
        end_point = (x[1], y[1])

        return cv2.line(img.copy(), start_point, end_point, color, thickness)

    @staticmethod
    def intersection(
        dot: np.ndarray, img: np.ndarray, color: Tuple[int, int, int] = Color.red
    ) -> np.ndarray:
        """
        Marks an intersection point on the image.

        Args:
            dot: Coordinates of the point (x, y).
            img: The input image.
            color: Color of the point in BGR format.

        Returns:
            The image with the point marked.
        """
        img_copy = img.copy()
        x, y = int(dot[0]), int(dot[1])
        img_copy[y, x, :] = color

        return img_copy

    @staticmethod
    def draw_cross(
        img: np.ndarray,
        center: Tuple[int, int],
        color: Tuple[int, int, int] = Color.red,
        size: int = 10,
        thickness: int = 1,
    ) -> np.ndarray:
        """
        Draws a cross at a specified location on the image.

        Args:
            img: The input image.
            center: Coordinates of the center point (x, y).
            color: Color of the cross in BGR format.
            size: Size of the cross arms.
            thickness: Thickness of the cross lines.

        Returns:
            The image with the cross drawn.
        """
        img_copy = img.copy()
        x, y = center
        img_copy = cv2.line(img_copy, (x - size, y), (x + size, y), color, thickness)
        img_copy = cv2.line(img_copy, (x, y - size), (x, y + size), color, thickness)

        return img_copy


class Text:
    @staticmethod
    def put_text(
        text: str,
        image: np.ndarray,
        org: Tuple[int, int],
        color: Tuple[int, int, int] = (0, 0, 0),
        font_scale: float = 0.25,
    ) -> np.ndarray:
        """
        Puts text on the image.

        Args:
            text: Text string to put on the image.
            image: The input image.
            org: Bottom-left corner of the text string in the image (x, y).
            color: Color of the text in BGR format.
            font_scale: Font scale factor that is multiplied by the font-specific base size.

        Returns:
            The image with text.
        """
        font = cv2.FONT_HERSHEY_DUPLEX
        thickness = 1

        return cv2.putText(
            image.copy(), text, org, font, font_scale, color, thickness, cv2.LINE_AA
        )


class LineDrawing:
    """Line and curve drawing utilities."""

    @staticmethod
    def draw_lsd_lines(
        lines: np.ndarray,
        img: np.ndarray,
        output_path: str,
        lines_all: Optional[np.ndarray] = None,
        thickness: int = 3,
    ) -> None:
        """
        Draws LSD (Line Segment Detector) lines on the image and saves it.

        Args:
            lines: Array of lines to be drawn.
            img: The input image.
            output_path: Path to save the output image.
            lines_all: Optional array of all lines to be drawn in a different color.
            thickness: Thickness of the lines.

        Returns:
            None
        """
        drawn_img = img.copy()

        if lines_all is not None:
            for line in lines_all:
                x1, y1, x2, y2 = line.ravel()
                cv2.line(
                    drawn_img,
                    (int(x1), int(y1)),
                    (int(x2), int(y2)),
                    Color.red,
                    thickness,
                )

        for line in lines:
            x1, y1, x2, y2 = line.ravel()
            cv2.line(
                drawn_img, (int(x1), int(y1)), (int(x2), int(y2)), Color.blue, thickness
            )

        # resized_img = resize_image_using_pil_lib(drawn_img, 640, 640)
        cv2.imwrite(output_path, drawn_img)

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

    @staticmethod
    def draw_lines(
        lines: np.ndarray,
        img: np.ndarray,
        output_path: str,
        lines_all: Optional[np.ndarray] = None,
        thickness: int = 1,
    ) -> None:
        """
        Draws extended lines on the image and saves it.

        Args:
            lines: Array of lines to be drawn.
            img: The input image.
            output_path: Path to save the output image.
            lines_all: Optional array of all lines to be drawn in a different color.
            thickness: Thickness of the lines.

        Returns:
            None
        """
        drawn_img = np.zeros_like(img)
        h, w = drawn_img.shape[:2]

        if lines_all is not None:
            for line in lines_all:
                x1, y1, x2, y2 = line.ravel()
                intersections = compute_intersection_with_block_boundaries(
                    np.array([x1, y1]), np.array([x2, y2]), img
                )
                valid_points = [
                    (intersections[i], intersections[i + 1])
                    for i in range(0, len(intersections), 2)
                    if intersections[i] is not None and intersections[i + 1] is not None
                ]
                if len(valid_points) >= 2:
                    x_start, y_start = valid_points[0]
                    x_end, y_end = valid_points[1]
                    drawn_img = LineDrawing.draw_line(
                        x_start,
                        y_start,
                        x_end,
                        y_end,
                        drawn_img,
                        thickness,
                        Color.white,
                    )

        for line in lines:
            x1, y1, x2, y2 = line.ravel()
            intersections = compute_intersection_with_block_boundaries(
                np.array([x1, y1]), np.array([x2, y2]), img
            )
            valid_points = [
                (intersections[i], intersections[i + 1])
                for i in range(0, len(intersections), 2)
                if intersections[i] is not None and intersections[i + 1] is not None
            ]
            if len(valid_points) >= 2:
                x_start, y_start = valid_points[0]
                x_end, y_end = valid_points[1]
                drawn_img = LineDrawing.draw_line(
                    x_start, y_start, x_end, y_end, drawn_img, thickness, Color.white
                )
        max_val = drawn_img.max()

        if max_val == 0:
            max_val = 1

        drawn_img = (drawn_img / max_val) * 255
        drawn_img = np.clip(drawn_img, 0, 255).astype(np.uint8)
        # resized_img = resize_image_using_pil_lib(drawn_img, 640, 640)
        cv2.imwrite(output_path, drawn_img)
