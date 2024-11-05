from typing import Tuple, Optional, List


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

    def __init__(self) -> None:
        """
        Initializes the Color class with a list of colors for cycling.

        Args:
            None

        Returns:
            None
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

        Args:
            None

        Returns:
            Tuple[int, int, int]: BGR tuple for the next color in the list.
        """
        self.idx = (self.idx + 1) % len(self.list)

        return self.list[self.idx]
