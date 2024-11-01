from typing import List, Optional
import numpy as np
import cv2

from ..geometry.node import Node
from ..geometry.chain import Chain, EndPoints, TypeChains
from ..geometry.geometry_utils import euclidean_distance_between_nodes
from ..visualization.drawing import Color, Drawing
from ..analysis.interpolation_nodes import (
    generate_nodes_list_between_two_radial_distances,
)


class VirtualBandGenerator:
    """
    Class for generating a virtual band between two chains.

    It also incorporates a method to check if a chain is inside the band.
    """

    DOWN = 0
    INSIDE = 1
    UP = 2

    def __init__(
        self,
        l_nodes: List[Node],
        ch_j: Chain,
        ch_k: Chain,
        endpoint: EndPoints,
        ch_i: Optional[Chain] = None,
        band_width: Optional[float] = None,
        debug: bool = False,
        inf_band: Optional[List[Node]] = None,
        sup_band: Optional[List[Node]] = None,
        domain: Optional[List[float]] = None,
    ):
        """
        Initializes an VirtualBandGenerator instance.

        Args:
            l_nodes (List[Node]): List of interpolated nodes between the two chains plus the two endpoints.
            ch_j (Chain): First chain to compute the band.
            ch_k (Chain): Second chain to compute the band.
            endpoint (EndPoints): Endpoint of ch_j.
            ch_i (Optional[Chain]): Support chain of ch_j and ch_k.
            band_width (Optional[float]): Band width as a percentage of the distance between ch_j and support chain (ch_i).
            debug (bool): If True, debugging information will be used.
            inf_band (Optional[List[Node]]): Lower band limit nodes.
            sup_band (Optional[List[Node]]): Upper band limit nodes.
            domain (Optional[List[float]]): Domain of interpolation.
        """
        if band_width is None:
            band_width = 0.05 if ch_i and ch_i.type == TypeChains.center else 0.1

        self.l_nodes = l_nodes
        self.ch_j = ch_j
        self.ch_k = ch_k
        self.endpoint = endpoint
        self.ch_i = ch_i
        params = {
            "y": self.ch_j.center[1],
            "x": self.ch_j.center[0],
            "angle": 0,
            "radial_distance": 0,
            "chain_id": -1,
        }
        self.center = Node(**params)

        ext1 = self.ch_j.extB if endpoint == EndPoints.B else self.ch_j.extA
        ext1_support = (
            self.ch_i.get_node_by_angle(ext1.angle)
            if self.ch_i is not None
            else self.center
        )
        ext2 = self.ch_k.extB if endpoint == EndPoints.A else self.ch_k.extA
        ext2_support = (
            self.ch_i.get_node_by_angle(ext2.angle)
            if self.ch_i is not None
            else self.center
        )
        delta_r1 = euclidean_distance_between_nodes(ext1, ext1_support)
        delta_r2 = euclidean_distance_between_nodes(ext2, ext2_support)
        self.inf_cand = delta_r2 * (1 - band_width)
        self.sup_cand = delta_r2 * (1 + band_width)
        self.inf_orig = delta_r1 * (1 - band_width)
        self.sup_orig = delta_r1 * (1 + band_width)

        if not debug:
            self.generate_band()
        else:
            self.inf_band = inf_band
            self.sup_band = sup_band
            self.interpolation_domain = domain

    def generate_band_limit(self, r2: float, r1: float, total_nodes: int) -> List[Node]:
        """
        Generates the band limit nodes between two radial distances.

        Args:
            r2 (float): Second radial distance.
            r1 (float): First radial distance.
            total_nodes (int): Total number of nodes.

        Returns:
            List[Node]: List of generated nodes for the band limit.
        """
        interpolation_domain = [node.angle for node in self.l_nodes]
        endpoint_cad2 = self.l_nodes[-1]
        support_node2 = (
            self.ch_i.get_node_by_angle(endpoint_cad2.angle)
            if self.ch_i is not None
            else self.center
        )
        sign = (
            -1 if support_node2.radial_distance > endpoint_cad2.radial_distance else +1
        )
        generated_dots = generate_nodes_list_between_two_radial_distances(
            r2,
            r1,
            total_nodes,
            interpolation_domain,
            self.ch_k.center,
            sign,
            self.ch_i,
            self.ch_k,
        )
        self.interpolation_domain = interpolation_domain

        return generated_dots

    def generate_band(self) -> None:
        """
        Generates the lower and upper bands based on the original and candidate radial distances.
        """
        total_nodes = len(self.l_nodes)
        r1 = self.sup_orig
        r2 = self.sup_cand
        self.sup_band = self.generate_band_limit(r2, r1, total_nodes)
        r1 = self.inf_orig
        r2 = self.inf_cand
        self.inf_band = self.generate_band_limit(r2, r1, total_nodes)

    @staticmethod
    def mean_radial_in_node_list(node_list: List[Node]) -> float:
        """
        Computes the mean radial distance in a list of nodes.

        Args:
            node_list (List[Node]): List of nodes.

        Returns:
            float: Mean radial distance.
        """
        return np.mean([node.radial_distance for node in node_list])

    def is_dot_in_band(self, node: Node) -> int:
        """
        Determines the relative position of a node with respect to the band.

        Args:
            node (Node): Node to check.

        Returns:
            int: Relative position (DOWN, INSIDE, or UP).
        """
        inf_mean_radii = self.mean_radial_in_node_list(self.inf_band)
        sup_mean_radii = self.mean_radial_in_node_list(self.sup_band)
        inner_band = self.inf_band if inf_mean_radii < sup_mean_radii else self.sup_band
        outer_band = self.sup_band if inf_mean_radii < sup_mean_radii else self.inf_band
        lowest = [n for n in inner_band if n.angle == node.angle][0]
        highest = [n for n in outer_band if n.angle == node.angle][0]

        if node.radial_distance <= lowest.radial_distance:
            relative_position = VirtualBandGenerator.DOWN
        elif highest.radial_distance >= node.radial_distance >= lowest.radial_distance:
            relative_position = VirtualBandGenerator.INSIDE
        else:
            relative_position = VirtualBandGenerator.UP

        return relative_position

    def is_chain_in_band(self, chain: Chain) -> bool:
        """
        Checks if a chain is inside the band.

        Args:
            chain (Chain): Chain to check.

        Returns:
            bool: True if the chain is inside the band, False otherwise.
        """
        node_chain_in_interval = [
            node for node in chain.l_nodes if node.angle in self.interpolation_domain
        ]
        prev_status = None

        for node in node_chain_in_interval:
            res = self.is_dot_in_band(node)
            if res == VirtualBandGenerator.INSIDE:
                return True
            if prev_status is not None and prev_status != res:
                return True
            prev_status = res

        return False

    def generate_chain_from_node_list(self, l_node: List[Node]) -> Chain:
        """
        Generates a chain from a list of nodes.

        Args:
            l_node (List[Node]): List of nodes.

        Returns:
            Chain: Generated chain.
        """
        chain = Chain(
            chain_id=l_node[0].chain_id,
            center=self.ch_j.center,
            img_height=self.ch_j.img_height,
            img_width=self.ch_j.img_width,
            nr=self.ch_j.nr,
        )
        chain.add_nodes_list(l_node)

        return chain

    def draw_band(self, img: np.ndarray, overlapping_chain: List[Chain]) -> np.ndarray:
        """
        Draws the band and the overlapping chains on an image.

        Args:
            img (np.ndarray): Image to draw on.
            overlapping_chain (List[Chain]): List of overlapping chains.

        Returns:
            np.ndarray: Image with the band and chains drawn.
        """
        img = Drawing.chain(
            self.generate_chain_from_node_list(self.inf_band), img, color=Color.orange
        )
        img = Drawing.chain(
            self.generate_chain_from_node_list(self.sup_band), img, color=Color.maroon
        )
        img = Drawing.chain(self.ch_j, img, color=Color.blue)
        img = Drawing.chain(self.ch_k, img, color=Color.yellow)

        if self.ch_i is not None:
            img = Drawing.chain(self.ch_i, img, color=Color.red)
        for chain in overlapping_chain:
            img = Drawing.chain(chain, img, color=Color.purple)

        return img
