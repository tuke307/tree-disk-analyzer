from ..geometry.chain import Chain


class Set:
    def __init__(self, angular_distance: float, cad: Chain) -> None:
        """
        Set class constructor

        Args:
            angular_distance (float): Angular distance between two points
            cad (Chain): Chain object

        Returns:
            None
        """
        self.distance = angular_distance
        self.cad = cad
