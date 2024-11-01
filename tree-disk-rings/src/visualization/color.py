from typing import List, Tuple
from itertools import cycle


class Color:
    """Class representing various colors in BGR format."""

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
        Initializes a Color instance with a cyclic iterator of colors.
        """
        self.list: List[Tuple[int, int, int]] = [
            self.yellow,
            self.red,
            self.blue,
            self.dark_yellow,
            self.cyan,
            self.orange,
            self.purple,
            self.maroon,
        ]
        self.color_cycle = cycle(self.list)

    def get_next_color(self) -> Tuple[int, int, int]:
        """
        Returns the next color in the cyclic iterator.

        Returns:
            Tuple[int, int, int]: The next color in BGR format.
        """
        return next(self.color_cycle)
