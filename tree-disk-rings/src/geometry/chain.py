from enum import Enum
from typing import List, Optional, Tuple, Any

import numpy as np

from ..geometry.node import Node


class TypeChains(Enum):
    center = 0
    normal = 1
    border = 2


class ClockDirection(Enum):
    clockwise = 0
    anti_clockwise = 1


class EndPoints(Enum):
    A = 0
    B = 1


class ChainLocation(Enum):
    inwards = 0
    outwards = 1


class Chain:
    def __init__(
        self,
        chain_id: int,
        nr: int,
        center: Tuple[float, float],
        img_height: int,
        img_width: int,
        type: TypeChains = TypeChains.normal,
        A_outward: Optional[Node] = None,
        A_inward: Optional[Node] = None,
        B_outward: Optional[Node] = None,
        B_inward: Optional[Node] = None,
    ) -> None:
        """
        Represents a chain of nodes.

        Args:
            chain_id (int): Identifier for the chain.
            nr (int): Number of rays.
            center (Tuple[float, float]): Center coordinates (x, y).
            img_height (int): Image height.
            img_width (int): Image width.
            type (TypeChains): Type of the chain.
            A_outward (Optional[Node]): Outward node at endpoint A.
            A_inward (Optional[Node]): Inward node at endpoint A.
            B_outward (Optional[Node]): Outward node at endpoint B.
            B_inward (Optional[Node]): Inward node at endpoint B.

        Returns:
            None
        """
        self.l_nodes: List[Node] = []
        self.id = chain_id
        self.size = 0
        self.nr = nr
        self.extA: Optional[Node] = None
        self.extB: Optional[Node] = None
        self.type = type
        self.A_outward = A_outward
        self.A_inward = A_inward
        self.B_outward = B_outward
        self.B_inward = B_inward

        # Less important attributes
        self.center = center  # center of the disk (pith pixel location)
        self.img_height = img_height  # image height
        self.img_width = img_width  # image width
        self.label_id = chain_id  # debug purpose

    def __eq__(self, other: Any) -> bool:
        """
        Compares two chains for equality.

        Args:
            other (Any): Object to compare to.

        Returns:
            bool: True if the chains are equal, False otherwise.
        """
        return (
            isinstance(other, Chain) and self.id == other.id and self.size == other.size
        )

    def is_closed(self, threshold: float = 0.95) -> bool:
        """
        Checks if the chain is closed based on the threshold.

        Args:
            threshold (float): Threshold ratio for being considered closed.

        Returns:
            bool: True if the chain is closed, False otherwise.
        """
        return len(self.l_nodes) >= threshold * self.nr

    def sort_dots(
        self, direction: ClockDirection = ClockDirection.clockwise
    ) -> List[Node]:
        """
        Returns the nodes sorted in the specified direction.

        Args:
            direction (ClockDirection): Direction to sort the nodes.

        Returns:
            List[Node]: Sorted list of nodes.
        """
        return (
            self.clockwise_sorted_dots
            if direction == ClockDirection.clockwise
            else self.clockwise_sorted_dots[::-1]
        )

    def _sort_dots(
        self, direction: ClockDirection = ClockDirection.clockwise
    ) -> List[Node]:
        """
        Sorts the nodes in the chain in the specified direction.

        Args:
            direction (ClockDirection): Direction to sort the nodes.

        Returns:
            List[Node]: Sorted list of nodes.
        """
        clock_wise_sorted_dots = []
        step = 360 / self.nr
        angle_k = (
            self.extB.angle
            if direction == ClockDirection.clockwise
            else self.extA.angle
        )
        while len(clock_wise_sorted_dots) < self.size:
            dot = self.get_node_by_angle(angle_k)
            assert dot is not None
            assert dot.chain_id == self.id
            clock_wise_sorted_dots.append(dot)
            angle_k = (
                (angle_k - step) % 360
                if direction == ClockDirection.clockwise
                else (angle_k + step) % 360
            )
        return clock_wise_sorted_dots

    def __repr__(self) -> str:
        """
        Returns a string representation of the chain.

        Args:
            None

        Returns:
            str: String representation of the chain.
        """
        return f"(id_l:{self.label_id},id:{self.id}, size {self.size}"

    def __find_endpoints(self) -> bool:
        """
        Finds the endpoints of the chain.

        Args:
            None

        Returns:
            bool: True if endpoints changed, False otherwise.
        """
        diff = np.zeros(self.size)
        extA_init = self.extA
        extB_init = self.extB
        self.l_nodes.sort(key=lambda x: x.angle, reverse=False)
        diff[0] = (self.l_nodes[0].angle + 360 - self.l_nodes[-1].angle) % 360

        for i in range(1, self.size):
            diff[i] = self.l_nodes[i].angle - self.l_nodes[i - 1].angle

        border1 = diff.argmax()
        if border1 == 0:
            border2 = diff.shape[0] - 1
        else:
            border2 = border1 - 1

        self.extAind = border1
        self.extBind = border2

        change_border = (
            True
            if (extA_init is None or extB_init is None)
            or (
                extA_init != self.l_nodes[border1] or extB_init != self.l_nodes[border2]
            )
            else False
        )
        self.extA = self.l_nodes[border1]
        self.extB = self.l_nodes[border2]

        return change_border

    def add_nodes_list(self, l_nodes: List[Node]) -> bool:
        """
        Adds a list of nodes to the chain.

        Args:
            l_nodes (List[Node]): List of nodes to add.

        Returns:
            bool: True if endpoints changed after adding nodes, False otherwise.
        """
        self.l_nodes += l_nodes
        change_border = self.update()
        return change_border

    def update(self) -> bool:
        """
        Updates the chain after adding nodes.

        Args:
            None

        Returns:
            bool: True if endpoints changed, False otherwise.
        """
        self.size = len(self.l_nodes)
        if self.size > 1:
            change_border = self.__find_endpoints()
            self.clockwise_sorted_dots = self._sort_dots()
        else:
            raise Exception("Chain must have at least two nodes.")

        return change_border

    def get_nodes_coordinates(self) -> Tuple[np.array, np.array]:
        """
        Gets the coordinates of the nodes in the chain.

        Args:
            None

        Returns:
            Tuple[np.array, np.array]: Arrays of x and y coordinates.
        """
        x = [dot.x for dot in self.l_nodes]
        y = [dot.y for dot in self.l_nodes]
        x_rot = np.roll(x, -self.extAind)
        y_rot = np.roll(y, -self.extAind)

        return np.array(x_rot), np.array(y_rot)

    def get_dot_angle_values(self) -> List[float]:
        """
        Gets the angle values of the nodes in the chain.

        Args:
            None

        Returns:
            List[float]: List of angle values.
        """
        return [dot.angle for dot in self.l_nodes]

    def get_node_by_angle(self, angle: float) -> Optional[Node]:
        """
        Retrieves a node by its angle.

        Args:
            angle (float): Angle to search for.

        Returns:
            Optional[Node]: The node with the specified angle, or None if not found.
        """
        from ..geometry.geometry_utils import get_node_from_list_by_angle

        return get_node_from_list_by_angle(self.l_nodes, angle)

    def change_id(self, index: int) -> int:
        """
        Changes the ID of the chain and its nodes.

        Args:
            index (int): New ID for the chain.

        Returns:
            int: 0 upon completion.
        """
        for dot in self.l_nodes:
            dot.chain_id = index
        self.id = index
        return 0

    def to_array(
        self,
    ) -> Tuple[np.array, np.array, np.array]:
        """
        Returns nodes coordinates in a numpy array, along with endpoint coordinates.

        Args:
            None

        Returns:
            Tuple[np.array, np.array, np.array]:
                nodes (np.ndarray): Coordinates of nodes.
                c1a (np.array): Coordinates of extA.
                c1b (np.array): Coordinates of extB.
        """
        x1, y1 = self.get_nodes_coordinates()
        nodes = np.vstack((x1, y1)).T
        c1a = np.array([self.extA.x, self.extA.y], dtype=float)
        c1b = np.array([self.extB.x, self.extB.y], dtype=float)

        return nodes.astype(float), c1a, c1b
