import matplotlib.pyplot as plt

from ..geometry.chain import Chain, EndPoints, ClockDirection
from ..geometry.node import Node
from ..analysis.interpolation_nodes import domain_interpolation
from ..geometry.geometry_utils import euclidean_distance_between_nodes

from typing import List


class ChainNeighbourhood:
    """
    Class to compute and store the total nodes of a chain and the candidate chains to connect to it.

    It generates the virtual nodes to compute the similarity condition.
    """

    def __init__(
        self,
        src_chain: Chain,
        dst_chain: Chain,
        support_chain: Chain,
        endpoint: EndPoints,
        n_nodes: int = 20,
    ):
        """
        Initializes a ChainNeighbourhood instance.

        Args:
            src_chain (Chain): Source chain to be connected.
            dst_chain (Chain): Destination chain to be connected.
            support_chain (Chain): Support chain to be used to generate the virtual nodes.
            endpoint (EndPoints): Endpoint of the source chain.
            n_nodes (int): Number of nodes to be considered in the total nodes.
        """
        self.virtual_nodes = self.generate_virtual_nodes_between_two_chains(
            src_chain, dst_chain, support_chain, endpoint
        )
        self.src_endpoint = (
            src_chain.extA if endpoint == EndPoints.A else src_chain.extB
        )
        self.dst_endpoint = (
            dst_chain.extA if endpoint == EndPoints.B else dst_chain.extB
        )
        self.endpoint_and_virtual_nodes = (
            [self.src_endpoint] + self.virtual_nodes + [self.dst_endpoint]
        )
        self.radial_distance_endpoints_to_support = (
            self.radial_distance_between_nodes_belonging_to_same_ray(
                [self.src_endpoint, self.dst_endpoint], support_chain
            )
        )
        self.radial_distance_virtual_nodes_to_support = (
            self.radial_distance_between_nodes_belonging_to_same_ray(
                self.virtual_nodes, support_chain
            )
        )

        self.src_chain_nodes = (
            src_chain.sort_dots(direction=ClockDirection.anti_clockwise)[:n_nodes]
            if endpoint == EndPoints.A
            else src_chain.sort_dots(direction=ClockDirection.clockwise)[:n_nodes]
        )
        self.dst_chain_nodes = (
            dst_chain.sort_dots(direction=ClockDirection.clockwise)[:n_nodes]
            if endpoint == EndPoints.A
            else dst_chain.sort_dots(direction=ClockDirection.anti_clockwise)[:n_nodes]
        )
        self.set_i = self.radial_distance_between_nodes_belonging_to_same_ray(
            self.src_chain_nodes, support_chain
        )
        self.set_k = self.radial_distance_between_nodes_belonging_to_same_ray(
            self.dst_chain_nodes, support_chain
        )

        if endpoint == EndPoints.B:
            self.neighbourhood_nodes = (
                self.src_chain_nodes[::-1] + self.virtual_nodes + self.dst_chain_nodes
            )
        else:
            self.neighbourhood_nodes = (
                self.dst_chain_nodes[::-1]
                + self.virtual_nodes[::-1]
                + self.src_chain_nodes
            )

    def draw_neighbourhood(self, name: str) -> None:
        """
        Draws the neighbourhood radial distances.

        Args:
            name (str): Filename to save the plot.
        """
        r = [node.radial_distance for node in self.neighbourhood_nodes]
        plt.figure()
        plt.plot(r, "b")
        plt.savefig(name)
        plt.close()

    def generate_virtual_nodes_between_two_chains(
        self,
        src_chain: Chain,
        dst_chain: Chain,
        support_chain: Chain,
        endpoint: EndPoints,
    ) -> List[Node]:
        """
        Generates virtual nodes between two chains using a support chain.

        Args:
            src_chain (Chain): Source chain to be connected.
            dst_chain (Chain): Destination chain to be connected.
            support_chain (Chain): Support chain used to generate the virtual nodes.
            endpoint (EndPoints): Endpoint of the source chain.

        Returns:
            List[Node]: List of virtual nodes.
        """
        virtual_nodes = []
        cad1_endpoint = src_chain.extA if endpoint == EndPoints.A else src_chain.extB
        cad2_endpoint = dst_chain.extB if endpoint == EndPoints.A else dst_chain.extA

        domain_interpolation(
            support_chain,
            cad1_endpoint,
            cad2_endpoint,
            endpoint,
            src_chain,
            virtual_nodes,
        )

        return virtual_nodes

    def radial_distance_between_nodes_belonging_to_same_ray(
        self, node_list: List[Node], support_chain: Chain
    ) -> List[float]:
        """
        Computes radial distances between nodes belonging to the same ray and a support chain.

        Args:
            node_list (List[Node]): List of nodes.
            support_chain (Chain): Support chain.

        Returns:
            List[float]: List of radial distances between nodes and support chain nodes.
        """
        radial_distances = []

        for node in node_list:
            support_node = support_chain.get_node_by_angle(node.angle)
            if support_node is None:
                break
            radial_distances.append(
                euclidean_distance_between_nodes(support_node, node)
            )

        return radial_distances
