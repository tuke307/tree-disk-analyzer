import cv2
import numpy as np
from shapely.geometry import Polygon
from ..visualization.drawing import Drawing
from ..geometry.chain import Chain


class Ring:
    def __init__(self, chain: Chain, id: int) -> None:
        """
        Initializes a Ring object.

        Args:
            chain (Chain): Chain object.
            id (int): Identifier of the ring.

        Returns:
            None
        """
        # Create a list of points (coordinates) from the sorted dots in the chain
        lista_pts = [[node.x, node.y] for node in chain.sort_dots()]
        self.id = id

        # Store the Polygon as an attribute
        self.geometry = Polygon(lista_pts)

    def draw(self, image: np.ndarray) -> np.ndarray:
        """
        Draws the ring on an image.

        Args:
            image (np.ndarray): Image on which to draw.

        Returns:
            np.ndarray: Image with the ring drawn.
        """
        x, y = self.geometry.exterior.coords.xy
        lista_pts = [[i, j] for i, j in zip(y, x)]
        pts = np.ndarray(lista_pts, np.int32)

        pts = pts.reshape((-1, 1, 2))
        is_closed = True

        # Blue color in BGR
        color = (255, 0, 0)

        # thickness of 2 px
        thickness = 1

        # Using cv2.polylines() method
        # Draw a Blue polygon with
        # thickness of 1 px
        image = cv2.polylines(image, [pts], is_closed, color, thickness)

        image = Drawing.put_text(f"{self.id}", image, (int(y[0]), int(x[0])))

        return image
