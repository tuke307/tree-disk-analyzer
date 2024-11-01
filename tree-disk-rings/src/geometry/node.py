from typing import Any


class Node:
    def __init__(
        self, x: float, y: float, chain_id: int, radial_distance: float, angle: float
    ) -> None:
        """
        Node representing a point with coordinates, angle, and radial distance.

        Args:
            x (float): X-coordinate.
            y (float): Y-coordinate.
            chain_id (int): ID of the chain this node belongs to.
            radial_distance (float): Radial distance from center.
            angle (float): Angle in degrees.

        Returns:
            None
        """
        self.x = x
        self.y = y
        self.chain_id = chain_id
        self.radial_distance = radial_distance
        self.angle = angle

    def __repr__(self) -> str:
        """
        Representation of the node.

        Args:
            None

        Returns:
            str: Representation of the node
        """
        return f"({self.x},{self.y}) ang:{self.angle} radio:{self.radial_distance:0.2f} cad.id {self.chain_id}\n"

    def __str__(self) -> str:
        """
        String representation of the node.

        Args:
            None

        Returns:
            str: String representation of the node
        """
        return f"({self.x},{self.y}) ang:{self.angle} radio:{self.radial_distance:0.2f} id {self.chain_id}"

    def __eq__(self, other: Any) -> bool:
        """
        Compare two nodes.

        Args:
            other (Any): Node to compare

        Returns:
            bool: True if the nodes are equal, False otherwise
        """
        return (
            isinstance(other, Node)
            and self.x == other.x
            and self.y == other.y
            and self.angle == other.angle
        )
