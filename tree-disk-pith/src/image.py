import numpy as np
from PIL import Image
import cv2
from typing import Tuple, Optional, List

from src.geometry import Line


def compute_intersection_with_block_boundaries(
    p1: np.ndarray, p2: np.ndarray, img: np.ndarray
) -> Tuple[
    Optional[float],
    Optional[float],
    Optional[float],
    Optional[float],
    Optional[float],
    Optional[float],
    Optional[float],
    Optional[float],
]:
    """
    Computes the intersection points of the line defined by p1 and p2 with the boundaries of the image.

    Args:
        p1: First point as a NumPy array [x, y].
        p2: Second point as a NumPy array [x, y].
        img: The image array.

    Returns:
        A tuple containing intersection points (x1, y1, x2, y2, x3, y3, x4, y4) with the image boundaries.
    """
    # Get the image dimensions
    if img.ndim == 3:
        height, width, _ = img.shape
    else:
        height, width = img.shape

    a, b, c = Line.compute_line_coefficients(p1, p2)

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

    x1, y1 = Line.get_line_coordinates(a, b, c, x=x1)
    x2, y2 = Line.get_line_coordinates(a, b, c, x=x2)
    x3, y3 = Line.get_line_coordinates(a, b, c, y=y3)
    x4, y4 = Line.get_line_coordinates(a, b, c, y=y4)

    return x1, y1, x2, y2, x3, y3, x4, y4


class Color:
    """
    A class containing color constants in BGR format.

    Attributes:
        yellow: BGR tuple for yellow color.
        red: BGR tuple for red color.
        blue: BGR tuple for blue color.
        dark_yellow: BGR tuple for dark yellow color.
        cyan: BGR tuple for cyan color.
        orange: BGR tuple for orange color.
        purple: BGR tuple for purple color.
        maroon: BGR tuple for maroon color.
        green: BGR tuple for green color.
        white: BGR tuple for white color.
        black: BGR tuple for black color.
        gray_white: Intensity value for gray white.
        gray_black: Intensity value for gray black.
    """

    yellow = (0, 255, 255)
    red = (0, 0, 255)
    blue = (255, 0, 0)
    dark_yellow = (0, 204, 204)
    cyan = (255, 255, 0)
    orange = (0, 165, 255)
    purple = (255, 0, 255)
    maroon = (34, 34, 178)
    green = (0, 255, 0)
    white = (255, 255, 255)
    black = (0, 0, 0)
    gray_white = 255
    gray_black = 0

    def __init__(self):
        """
        Initializes the Color class with a list of colors for cycling.
        """
        self.list: List[Tuple[int, int, int]] = [
            Color.yellow,
            Color.red,
            Color.blue,
            Color.dark_yellow,
            Color.cyan,
            Color.orange,
            Color.purple,
            Color.maroon,
        ]
        self.idx: int = 0

    def get_next_color(self) -> Tuple[int, int, int]:
        """
        Cycles through the color list and returns the next color.

        Returns:
            A BGR tuple representing the next color.
        """
        self.idx = (self.idx + 1) % len(self.list)
        return self.list[self.idx]


class Drawing:
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
        resized_img = resize_image_using_pil_lib(drawn_img, 640, 640)
        cv2.imwrite(output_path, resized_img)

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
                    drawn_img = Line.draw_line(
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
                drawn_img = Line.draw_line(
                    x_start, y_start, x_end, y_end, drawn_img, thickness, Color.white
                )
        max_val = drawn_img.max()
        if max_val == 0:
            max_val = 1
        drawn_img = (drawn_img / max_val) * 255
        drawn_img = np.clip(drawn_img, 0, 255).astype(np.uint8)
        resized_img = resize_image_using_pil_lib(drawn_img, 640, 640)
        cv2.imwrite(output_path, resized_img)

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


def resize_image_using_pil_lib(
    im_in: np.ndarray, height_output: int, width_output: int, keep_ratio: bool = True
) -> np.ndarray:
    """
    Resizes the image using PIL library.

    Args:
        im_in: Input image as a NumPy array.
        height_output: Desired height of the output image.
        width_output: Desired width of the output image.
        keep_ratio: Whether to maintain the aspect ratio.

    Returns:
        The resized image as a NumPy array.
    """
    pil_img = Image.fromarray(im_in)
    resample_flag = Image.Resampling.LANCZOS

    if keep_ratio:
        aspect_ratio = pil_img.height / pil_img.width
        if pil_img.width > pil_img.height:
            height_output = int(width_output * aspect_ratio)
        else:
            width_output = int(height_output / aspect_ratio)

    pil_img = pil_img.resize((width_output, height_output), resample_flag)
    return np.array(pil_img)


def change_background_to_value(
    im_in: np.ndarray, mask: np.ndarray, value: int = 255
) -> np.ndarray:
    """
    Changes the background intensity to a specified value.

    Args:
        im_in: Input image.
        mask: Mask where non-zero values indicate background.
        value: The intensity value to set for the background.

    Returns:
        The image with background intensity changed.
    """
    im_out = im_in.copy()
    im_out[mask > 0] = value
    return im_out


def rgb2gray(img_r: np.ndarray) -> np.ndarray:
    """
    Converts an RGB image to grayscale.

    Args:
        img_r: Input RGB image.

    Returns:
        Grayscale image.
    """
    return cv2.cvtColor(img_r, cv2.COLOR_BGR2GRAY)


def change_background_intensity_to_mean(
    im_in: np.ndarray,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Changes the background intensity to the mean intensity of the non-background.

    Args:
        im_in: Input grayscale image with background intensity as 255.

    Returns:
        A tuple containing the image with background intensity changed and the background mask.
    """
    im_eq = im_in.copy()
    mask = np.where(im_in == 255, 1, 0)
    mean_intensity = np.mean(im_in[mask == 0])
    im_eq = change_background_to_value(im_eq, mask, int(mean_intensity))
    return im_eq, mask


def equalize_image_using_clahe(img_eq: np.ndarray) -> np.ndarray:
    """
    Equalizes the image using CLAHE algorithm.

    Args:
        img_eq: Input image to be equalized.

    Returns:
        Equalized image.
    """
    clahe = cv2.createCLAHE(clipLimit=10)
    return clahe.apply(img_eq)


def equalize(im_g: np.ndarray) -> np.ndarray:
    """
    Equalizes the image using CLAHE after adjusting background intensity.

    Args:
        im_g: Grayscale image.

    Returns:
        Equalized image.
    """
    im_pre, mask = change_background_intensity_to_mean(im_g)
    im_pre = equalize_image_using_clahe(im_pre)
    im_pre = change_background_to_value(im_pre, mask, Color.gray_white)
    return im_pre
