from typing import List

from ..geometry.chain import Chain
from ..geometry.node import Node


class ConnectParameters:
    """
    Class for grouping all the parameter from table 1 in the paper
    """

    iterations = 9
    params = {
        "th_radial_tolerance": [0.1, 0.2, 0.1, 0.2, 0.1, 0.2, 0.1, 0.2, 0.2],
        "neighbourhood_size": [10, 10, 22, 22, 45, 45, 22, 45, 45],
        "th_regular_derivative": [1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 2, 2, 2],
        "th_distribution_size": [2, 2, 3, 3, 3, 3, 2, 3, 3],
        "derivative_from_center": [
            False,
            False,
            False,
            False,
            False,
            False,
            True,
            True,
            True,
        ],
    }

    def __init__(self, ch_s: List[Chain], nodes_s: List[Node]) -> None:
        """
        Initialize the class with the border chain and the chains without the border chain.

        Args:
            ch_s (List[Chain]): list of chains
            nodes_s (List[Node]): list of nodes

        Returns:
            None
        """
        from ..analysis.connect_chains import extract_border_chain_from_list

        self.border_chain, self.ch_s_without_border, self.nodes_s_without_border = (
            extract_border_chain_from_list(ch_s, nodes_s)
        )

    def get_iteration_parameters(self, counter: int) -> dict:
        """
        Get the parameters for the next iteration.

        Args:
            counter (int): iteration counter

        Returns:
            Dict: parameters for the next iteration
        """
        iteration_params = {
            "th_radial_tolerance": self.params["th_radial_tolerance"][counter],
            "th_distribution_size": self.params["th_distribution_size"][counter],
            "neighbourhood_size": self.params["neighbourhood_size"][counter],
            "th_regular_derivative": self.params["th_regular_derivative"][counter],
            "derivative_from_center": self.params["derivative_from_center"][counter],
            "l_ch_s": (
                self.ch_s_without_border
                if counter < self.iterations - 1
                else self.ch_s_without_border + [self.border_chain]
            ),
            "l_nodes_s": (
                self.nodes_s_without_border
                if counter < self.iterations - 1
                else self.nodes_s_without_border + self.border_chain.l_nodes
            ),
        }

        if counter == self.iterations - 1:
            self.border_chain.change_id(len(self.ch_s_without_border))

        return iteration_params

    def update_list_for_next_iteration(
        self, ch_c: List[Chain], nodes_c: List[Node]
    ) -> None:
        """
        Update the list of chains and nodes for the next iteration.

        Args:
            ch_c (List[Chain]): list of chains
            nodes_c (List[Node]): list of nodes

        Returns:
            None
        """
        self.ch_s_without_border, self.nodes_s_without_border = ch_c, nodes_c
