from typing import Tuple

import cv2
import numpy as np
from typing import List


from ..visualization.color import Color


class Drawing:
    @staticmethod
    def circle(
        image: np.ndarray,
        center_coordinates: Tuple[int, int],
        thickness: int = -1,
        color: Tuple[int, int, int] = Color.black,
        radius: int = 3,
    ) -> np.ndarray:
        """
        Draws a circle on an image.

        Args:
            image (np.ndarray): The image on which to draw the circle.
            center_coordinates (Tuple[int, int]): The center coordinates of the circle.
            thickness (int): Thickness of the circle outline. Default is -1 (filled circle).
            color (Tuple[int, int, int]): Color of the circle in BGR format.
            radius (int): Radius of the circle.

        Returns:
            np.ndarray: The image with the drawn circle.
        """
        # Ensure the image has the correct data type
        if image.dtype != np.uint8:
            image = image.astype(np.uint8)

        image = cv2.circle(image, center_coordinates, radius, color, thickness)

        return image

    @staticmethod
    def put_text(
        text: str,
        image: np.ndarray,
        org: Tuple[int, int],
        color: Tuple[int, int, int] = (0, 0, 0),
        fontScale: float = 0.25,
    ) -> np.ndarray:
        """
        Places text on an image.

        Args:
            text (str): The text string to be drawn.
            image (np.ndarray): The image on which to draw the text.
            org (Tuple[int, int]): The bottom-left corner of the text string in the image.
            color (Tuple[int, int, int]): Color of the text in BGR format.
            fontScale (float): Font scale factor.

        Returns:
            np.ndarray: The image with the drawn text.
        """
        font = cv2.FONT_HERSHEY_DUPLEX
        thickness = 1
        image = cv2.putText(
            image, text, org, font, fontScale, color, thickness, cv2.LINE_AA
        )

        return image

    @staticmethod
    def intersection(
        dot: "Node",
        img: np.ndarray,
        color: Tuple[int, int, int] = Color.red,
    ) -> np.ndarray:
        """
        Marks an intersection point on an image.

        Args:
            dot (Node): The point to mark, expected to have attributes 'x' and 'y'.
            img (np.ndarray): The image on which to mark the point.
            color (Tuple[int, int, int]): Color of the mark in BGR format.

        Returns:
            np.ndarray: The image with the marked intersection.
        """
        from ..geometry.node import Node

        img[int(dot.y), int(dot.x), :] = color

        return img

    @staticmethod
    def curve(
        curve: "Curve",
        img: np.ndarray,
        color: Tuple[int, int, int] = (0, 255, 0),
        thickness: int = 1,
    ) -> np.ndarray:
        """
        Draws a curve on an image.

        Args:
            curve (Curve): The curve object, expected to have 'geometry.xy' attributes.
            img (np.ndarray): The image on which to draw the curve.
            color (Tuple[int, int, int]): Color of the curve in BGR format.
            thickness (int): Thickness of the curve lines.

        Returns:
            np.ndarray: The image with the drawn curve.
        """
        from ..geometry.curve import Curve

        y, x = curve.geometry.xy
        y = np.ndarray(y).astype(int)
        x = np.ndarray(x).astype(int)
        pts = np.vstack((x, y)).T
        isClosed = False
        img = cv2.polylines(img, [pts], isClosed, color, thickness)

        return img

    @staticmethod
    def chain(
        chain: "Chain",
        img: np.ndarray,
        color: Tuple[int, int, int] = (0, 255, 0),
        thickness: int = 5,
    ) -> np.ndarray:
        """
        Draws a chain of nodes on an image.

        Args:
            chain (Chain): The chain object, expected to have 'get_nodes_coordinates()' method.
            img (np.ndarray): The image on which to draw the chain.
            color (Tuple[int, int, int]): Color of the chain in BGR format.
            thickness (int): Thickness of the chain lines.

        Returns:
            np.ndarray: The image with the drawn chain.
        """
        from ..geometry.chain import Chain

        y, x = chain.get_nodes_coordinates()
        pts = np.vstack((y, x)).T.astype(int)
        isClosed = False
        img = cv2.polylines(img, [pts], isClosed, color, thickness)

        return img

    @staticmethod
    def radii(
        ray: "Ray",
        img: np.ndarray,
        color: Tuple[int, int, int] = (255, 0, 0),
        thickness: int = 1,
    ) -> np.ndarray:
        """
        Draws a radius line on an image.

        Args:
            ray (Radii): The radii object, expected to have 'geometry.xy' attributes.
            img (np.ndarray): The image on which to draw the radius.
            color (Tuple[int, int, int]): Color of the radius line in BGR format.
            thickness (int): Thickness of the radius line.

        Returns:
            np.ndarray: The image with the drawn radius.
        """
        from ..geometry.ray import Ray

        y, x = ray.geometry.xy
        y = np.ndarray(y).astype(int)
        x = np.ndarray(x).astype(int)
        start_point = (x[0], y[0])
        end_point = (x[1], y[1])
        image = cv2.line(img, start_point, end_point, color, thickness)

        return image

    @staticmethod
    def write_curves_to_image(
        curves_list: List["Curve"], img: np.ndarray
    ) -> np.ndarray:
        """
        Draws curves onto an image.

        Args:
            curves_list (List[Curve]): Array of curve points.
            img (np.ndarray): Image array.

        Returns:
            np.ndarray: Image with curves drawn.
        """
        from ..geometry.curve import Curve

        img_aux = np.full((img.shape[0], img.shape[1]), 255)

        for pix in curves_list:
            if pix[0] < 0 and pix[1] < 0:
                continue
            img_aux = Drawing.circle(img_aux, (int(pix[0]), int(pix[1])))

        return img_aux
