from typing import List

from ..geometry.chain import Chain


class ChainsBag:
    def __init__(self, inward_chain_set: List[Chain]) -> None:
        """
        Iterate over chains in a region.

        Args:
            inward_chain_set: list of chains in a region

        Returns:
            None
        """
        self.chain_set = inward_chain_set
        self.chains_id_already_selected = []

    def get_next_chain(self) -> Chain:
        """
        Get the next chain in the region.

        Returns:
            Chain: the next chain
        """
        next = None

        for chain in self.chain_set:
            if chain.id not in self.chains_id_already_selected:
                next = chain
                self.chains_id_already_selected.append(next.id)
                break

        return next
