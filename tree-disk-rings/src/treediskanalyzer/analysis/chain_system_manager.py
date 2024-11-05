import numpy as np
from pathlib import Path
from typing import List, Optional, Tuple

from ..geometry.geometry_utils import (
    copy_chain,
    euclidean_distance_between_nodes,
    get_chain_from_list_by_id,
    get_chains_within_angle,
)
from ..geometry.chain import Chain, EndPoints
from ..geometry.node import Node
from ..analysis.interpolation_nodes import domain_interpolation
from ..analysis.chain_analysis_tools import (
    exist_chain_overlapping,
)
from ..config import config


class ChainSystemManager:
    def __init__(
        self,
        l_ch: List[Chain],
        l_nodes: List[Node],
        M: np.ndarray,
        nr: int = 360,
        th_radial_tolerance: float = 0.1,
        th_distribution_size: int = 2,
        th_regular_derivative: float = 1.5,
        neighbourhood_size: int = 45,
        derivative_from_center: bool = False,
        debug: bool = False,
        counter: int = 0,
        save: Optional[str] = None,
        img: Optional[np.ndarray] = None,
    ) -> None:
        """
        Initialize the ChainSystemManager with the given parameters.

        Args:
            l_ch (List[Chain]): List of chains.
            l_nodes (List[Node]): List of nodes.
            M (np.ndarray): Matrix representing the system.
            cy (int): Y-coordinate of the center.
            cx (int): X-coordinate of the center.
            nr (int, optional): Number of radial divisions. Default is 360.
            th_radial_tolerance (float, optional): Radial tolerance threshold. Default is 0.1.
            th_distribution_size (int, optional): Distribution size threshold. Default is 2.
            th_regular_derivative (float, optional): Regular derivative threshold. Default is 1.5.
            neighbourhood_size (int, optional): Size of the neighbourhood. Default is 45.
            derivative_from_center (bool, optional): Whether to calculate derivative from center. Default is False.
            debug (bool, optional): Enable debugging. Default is False.
            counter (int, optional): Counter value. Default is 0.
            save (Optional[str], optional): Path to save the results. Default is None.
            img (Optional[np.ndarray], optional): Image array. Default is None.

        Returns:
            None
        """
        # initialization
        self.l_nodes_s = l_nodes
        self.l_ch_s = l_ch
        self.__sort_chain_list_and_update_relative_position()

        # system parameters
        self.nr = nr
        self.derivative_from_center = derivative_from_center
        self.th_distribution_size = th_distribution_size
        self.debug = debug
        self.neighbourhood_size = neighbourhood_size
        self.M = M
        self.center = [config.cy, config.cx]
        self.img = img
        self.height = img.shape[0]
        self.width = img.shape[1]
        self.next_chain_index = 0
        self.iterations_since_last_change = 0
        self.th_radial_tolerance = th_radial_tolerance
        self.label = "system_status"
        self.counter = counter
        self.th_regular_derivative = th_regular_derivative
        self.path = save

        if self.path is not None and self.debug:
            Path(self.path).mkdir(exist_ok=True)

    def get_common_chain_to_both_borders(self, chain: Chain) -> Optional[Chain]:
        """
        Args:
            chain (Chain): The chain to check for common chains to both borders.

        Returns:
            Optional[Chain]: The common chain to both borders if found, otherwise None.
        """
        chain_angle_domain = chain.get_dot_angle_values()
        angles_where_there_is_no_nodes = [
            angle
            for angle in np.arange(0, 360, 360 / self.nr)
            if angle not in chain_angle_domain
        ]
        angles_where_there_is_no_nodes += [chain.extA.angle, chain.extB.angle]
        chains_where_there_is_no_nodes = []
        for ch_i in self.l_ch_s:
            ch_i_angles = ch_i.get_dot_angle_values()
            if np.intersect1d(ch_i_angles, angles_where_there_is_no_nodes).shape[
                0
            ] == len(angles_where_there_is_no_nodes):
                chains_where_there_is_no_nodes.append(ch_i)

        if len(chains_where_there_is_no_nodes) == 0:
            return None

        nodes_in_ray_a = [
            cad.get_node_by_angle(chain.extA.angle)
            for cad in chains_where_there_is_no_nodes
        ]
        nodes_in_ray_a.sort(
            key=lambda x: euclidean_distance_between_nodes(x, chain.extA)
        )
        id_closest = nodes_in_ray_a[0].chain_id

        return get_chain_from_list_by_id(self.l_ch_s, id_closest)

    def compute_all_elements_needed_to_check_if_exist_chain_overlapping(
        self, chain: Chain
    ) -> Tuple[Optional[Chain], List[Node], EndPoints]:
        """
        Args:
            chain (Chain): The chain to check for overlapping.

        Returns:
            Tuple[Optional[Chain], List[Node], EndPoints]: The common chain, interpolated nodes plus endpoints, and endpoint type.
        """
        ch_i = self.get_common_chain_to_both_borders(chain)
        ch_j_endpoint_node = chain.extB
        ch_k_endpoint_node = chain.extA
        ch_j_endpoint_type = EndPoints.B

        interpolated_nodes = []  # domain interpolation function output
        chain_copy = copy_chain(chain)
        domain_interpolation(
            ch_i,
            ch_j_endpoint_node,
            ch_k_endpoint_node,
            ch_j_endpoint_type,
            chain_copy,
            interpolated_nodes,
        )
        interpolated_nodes_plus_endpoints = (
            [ch_j_endpoint_node] + interpolated_nodes + [ch_k_endpoint_node]
        )

        return ch_i, interpolated_nodes_plus_endpoints, ch_j_endpoint_type

    def fill_chain_if_there_is_no_overlapping(self, chain: Chain) -> None:
        """
        Algorithm 10 in the supplementary material. Complete chain if there is no overlapping.

        Args:
            chain (Chain): Chain to be completed if conditions are met.

        Returns:
            None
        """
        # Check if chain is too small or is full. If it is, return.
        threshold = 0.9
        if chain.size >= chain.nr or chain.size < threshold * chain.nr:
            return

        ch_i, l_nodes, endpoint_type = (
            self.compute_all_elements_needed_to_check_if_exist_chain_overlapping(chain)
        )

        # Algorithm 13 in the paper. Check if there is an overlapping chain.
        exist_chain = exist_chain_overlapping(
            self.l_ch_s, l_nodes, chain, chain, endpoint_type, ch_i
        )

        if exist_chain:
            return

        self.add_nodes_list_to_system(chain, l_nodes)

        return

    def continue_in_loop(self) -> bool:
        """
        Args:
            None

        Returns:
            bool: Whether the algorithm should continue in the loop.
        """
        # If iteration_sin_last_chain is equal to the number of chains, the algorithm stops. This means that
        # all chains have been iterated at least one time and no chains have been connected or interpolated.
        return self.iterations_since_last_change < len(self.l_ch_s)

    def get_next_chain(self) -> Chain:
        """
        Algorithm 9 in the supplementary material. Get next chain to be processed.

        Args:
            None

        Returns:
            Chain: Next supported chain.
        """
        ch_i = self.l_ch_s[self.next_chain_index]

        self.size_l_chain_init = len(self.l_ch_s)

        #  Algorithm 12 in the paper
        self.fill_chain_if_there_is_no_overlapping(ch_i)

        return ch_i

    def is_new_dot_valid(self, new_dot: Node) -> bool:
        """
        Args:
            new_dot (Node): The new dot to validate.

        Returns:
            bool: Whether the new dot is valid.
        """
        if new_dot in self.l_nodes_s:
            return False
        if (
            new_dot.x >= self.height
            or new_dot.y >= self.width
            or new_dot.x < 0
            or new_dot.y < 0
        ):
            return False

        return True

    def update_chain_neighbourhood(
        self, l_chains_to_update_neighborhood: List[Chain]
    ) -> None:
        """
        Args:
            l_chains_to_update_neighborhood (List[Chain]): List of chains to update the neighborhood.

        Returns:
            None
        """
        from ..analysis.connect_chains import get_inward_and_outward_visible_chains

        dummy_chain = None
        for chain_p in l_chains_to_update_neighborhood:
            border = EndPoints.A
            inward_chain, outward_chain, dot_border = (
                get_inward_and_outward_visible_chains(self.l_ch_s, chain_p, border)
            )

            chain_p.A_outward = (
                outward_chain if outward_chain is not None else dummy_chain
            )
            chain_p.A_inward = inward_chain if inward_chain is not None else dummy_chain
            border = EndPoints.B
            inward_chain, outward_chain, dot_border = (
                get_inward_and_outward_visible_chains(self.l_ch_s, chain_p, border)
            )
            chain_p.B_outward = (
                outward_chain if outward_chain is not None else dummy_chain
            )
            chain_p.B_inward = inward_chain if inward_chain is not None else dummy_chain

        return

    def add_nodes_list_to_system(self, chain: Chain, l_nodes: List[Node]) -> None:
        """
        Args:
            chain (Chain): The chain to which nodes will be added.
            l_nodes (List[Node]): List of nodes to be added to the system.

        Returns:
            None
        """
        processed_node_list = []
        for new_dot in l_nodes:
            if chain.id != new_dot.chain_id:
                raise

            processed_node_list.append(new_dot)
            if new_dot in self.l_nodes_s:
                continue

            self.l_nodes_s.append(new_dot)
            # 1.0 Update ch_i list intersection
            chain_id_intersecting, chains_over_radial_direction = (
                self._chains_id_over_radial_direction(new_dot.angle)
            )
            self.M[chain.id, chain_id_intersecting] = 1
            self.M[chain_id_intersecting, chain.id] = 1

            # 2.0 Update boundary chains above and below.
            dots_over_direction = [
                dot
                for chain in chains_over_radial_direction
                for dot in chain.l_nodes
                if dot.angle == new_dot.angle
            ]
            dots_over_direction.append(new_dot)
            dots_over_direction.sort(key=lambda x: x.radial_distance)
            idx_new_dot = dots_over_direction.index(new_dot)

            up_dot = (
                dots_over_direction[idx_new_dot + 1]
                if idx_new_dot < len(dots_over_direction) - 1
                else None
            )
            if up_dot is not None:
                up_chain = get_chain_from_list_by_id(
                    chain_list=chains_over_radial_direction, chain_id=up_dot.chain_id
                )
                if up_dot == up_chain.extA:
                    up_chain.A_inward = chain
                elif up_dot == up_chain.extB:
                    up_chain.B_inward = chain

            down_dot = dots_over_direction[idx_new_dot - 1] if idx_new_dot > 0 else None
            if down_dot is not None:
                down_chain = get_chain_from_list_by_id(
                    chain_list=chains_over_radial_direction, chain_id=down_dot.chain_id
                )
                if down_dot == down_chain.extA:
                    down_chain.A_outward = chain
                elif down_dot == down_chain.extB:
                    down_chain.B_outward = chain

        change_border = chain.add_nodes_list(processed_node_list)
        self.update_chain_neighbourhood([chain])

    @staticmethod
    def get_next_chain_index_in_list(
        chains_list: List[Chain], support_chain: Chain
    ) -> int:
        """
        Args:
            chains_list (List[Chain]): List of chains.
            support_chain (Chain): The support chain to find the next index for.

        Returns:
            int: The index of the next chain in the list.
        """
        return (chains_list.index(support_chain) + 1) % len(chains_list)

    def update_system_status(
        self, ch_i: Chain, l_s_outward: List[Chain], l_s_inward: List[Chain]
    ) -> int:
        """
        Algorithm 8 in the supplementary material. Update the system state after the iteration.

        Args:
            ch_i (Chain): Support chain in current iteration.
            l_s_outward (List[Chain]): Outward list of chains.
            l_s_inward (List[Chain]): Inward list of chains.

        Returns:
            int: Index of the next support chain to be processed.
        """
        # self.l_ch_s is an attribute of the self object.
        if self._system_status_change():
            self.l_ch_s.sort(key=lambda x: x.size, reverse=True)
            # Variable used to check if system status has changed in current iteration. If it has (variable is set to 0),
            # the algorithm continues one more iteration. If it has not (variable is increased by 1). Variable is used as
            # exit condition in the while loop (Algorithm 2, line 3, continue_in_loop method).
            self.iterations_since_last_change = 0

            l_current_iteration = [ch_i] + l_s_outward + l_s_inward

            l_current_iteration.sort(key=lambda x: x.size, reverse=True)

            longest_chain = l_current_iteration[0]

            if longest_chain.id == ch_i.id:
                next_chain_index = self.get_next_chain_index_in_list(self.l_ch_s, ch_i)
            else:
                next_chain_index = self.l_ch_s.index(longest_chain)

        else:
            next_chain_index = self.get_next_chain_index_in_list(self.l_ch_s, ch_i)
            # System status has not changed. Increase variable by 1.
            self.iterations_since_last_change += 1

        self.next_chain_index = next_chain_index

        return 0

    def _chains_id_over_radial_direction(
        self, angle: float
    ) -> Tuple[List[int], List[Chain]]:
        """
        Args:
            angle (float): The angle to find chains over radial direction.

        Returns:
            Tuple[List[int], List[Chain]]: List of chain IDs and chains in radial direction.
        """
        chains_in_radial_direction = get_chains_within_angle(angle, self.l_ch_s)
        chains_id_over_radial_direction = [cad.id for cad in chains_in_radial_direction]

        return chains_id_over_radial_direction, chains_in_radial_direction

    def __sort_chain_list_and_update_relative_position(self) -> None:
        """
        Args:
            None

        Returns:
            None
        """
        self.l_ch_s = sorted(self.l_ch_s, key=lambda x: x.size, reverse=True)
        self.update_chain_neighbourhood(self.l_ch_s)

    def _system_status_change(self) -> bool:
        """
        Args:
            None

        Returns:
            bool: Whether the system status has changed.
        """
        self.chain_size_at_the_end_of_iteration = len(self.l_ch_s)

        return self.size_l_chain_init > self.chain_size_at_the_end_of_iteration
