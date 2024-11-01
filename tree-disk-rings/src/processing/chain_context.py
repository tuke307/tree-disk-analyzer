from shapely.geometry import Point, LineString
from typing import List, Optional, Tuple

from ..geometry.ring import Ring
from ..geometry.chain import Chain
from ..geometry.geometry_utils import visualize_selected_ch_and_chains_over_image_


class ChainContext:
    def __init__(
        self,
        l_ch_c: List[Chain],
        idx_start: Optional[int],
        save_path: Optional[str] = None,
        img: Optional[str] = None,
        debug: bool = True,
    ):
        """
        Initialize the ChainContext object.

        Args:
            l_ch_c (List[Chain]): List of chains
            idx_start (Optional[int]): Starting index
            save_path (Optional[str], optional): Path to save images. Defaults to None.
            img (Optional[str], optional): Image path. Defaults to None.
            debug (bool, optional): Debug flag. Defaults to True.
        """
        self.l_within_chains = []
        self.neighbourhood_size = None
        self.debug = debug
        self.save_path = save_path
        self.img = img
        self.completed_chains = [cad for cad in l_ch_c if cad.size >= cad.nr]
        self.completed_chains, self.poly_completed_chains = (
            self._from_completed_chain_to_poly(self.completed_chains)
        )

        self.uncompleted_chains = [cad for cad in l_ch_c if cad.size < cad.nr]
        self.uncompleted_chains_poly = self._from_uncompleted_chains_to_poly(
            self.uncompleted_chains
        )
        self.idx = 1 if idx_start is None else idx_start

    def get_inward_outward_ring(
        self, idx: int
    ) -> Tuple[Optional[Ring], Optional[Ring]]:
        """
        Get the inward and outward rings based on the index.

        Args:
            idx (int): Index to get the rings

        Returns:
            Tuple[Optional[Ring], Optional[Ring]]: Tuple of inward and outward rings
        """
        self.neighbourhood_size = 45
        outward_ring = None
        inward_ring = None

        if len(self.poly_completed_chains) > idx > 0:
            inward_ring = self.poly_completed_chains[idx - 1]
            outward_ring = self.poly_completed_chains[idx]

        return inward_ring, outward_ring

    def update(self) -> None:
        """
        Update the context. The context is updated when the algorithm is executed over a new region.
        """
        from ..processing.postprocessing import (
            search_shapely_inward_chain,
            from_shapely_to_chain,
        )

        inward_poly_ring, outward_poly_ring = self.get_inward_outward_ring(self.idx)
        shapely_inward_chain_subset = search_shapely_inward_chain(
            self.uncompleted_chains_poly, outward_poly_ring, inward_poly_ring
        )
        self.l_within_chains = from_shapely_to_chain(
            self.uncompleted_chains_poly,
            self.uncompleted_chains,
            shapely_inward_chain_subset,
        )

        self.inward_ring, self.outward_ring = self._from_shapely_ring_to_chain(
            inward_poly_ring, outward_poly_ring
        )

    def exit(self) -> bool:
        """
        Increment the index and check if it exceeds the length of completed chains.

        Returns:
            bool: True if index exceeds the length of completed chains, otherwise False
        """
        self.idx += 1
        if self.idx >= len(self.completed_chains):
            return True

        return False

    def drawing(self, iteration: int) -> None:
        """
        Visualize and save the selected chains and rings over the image.

        Args:
            iteration (int): Iteration number for the filename

        Returns:
            None
        """
        visualize_selected_ch_and_chains_over_image_(
            self.l_within_chains
            + [
                chain
                for chain in [self.inward_ring, self.outward_ring]
                if chain is not None
            ],
            [],
            img=self.img,
            filename=f"{self.save_path}/{iteration}_0.png",
        )

    def _from_shapely_ring_to_chain(
        self, poly_ring_inward: Optional[Ring], poly_ring_outward: Optional[Ring]
    ) -> Tuple[Optional[Ring], Optional[Ring]]:
        """
        Convert shapely rings to chain rings.

        Args:
            poly_ring_inward (Optional[Ring]): Inward shapely ring
            poly_ring_outward (Optional[Ring]): Outward shapely ring

        Returns:
            Tuple[Optional[Ring], Optional[Ring]]: Tuple of inward and outward chain rings
        """
        inward_chain_ring = None
        outward_chain_ring = None

        if poly_ring_inward is not None:
            inward_chain_ring = self.completed_chains[
                self.poly_completed_chains.index(poly_ring_inward)
            ]

        if poly_ring_outward is not None:
            outward_chain_ring = self.completed_chains[
                self.poly_completed_chains.index(poly_ring_outward)
            ]

        return inward_chain_ring, outward_chain_ring

    def sort_list_by_index_array(self, indexes: List[int], list: List) -> List:
        """
        Sort a list based on the given indexes.

        Args:
            indexes (List[int]): List of indexes
            list_position (List): List to be sorted

        Returns:
            List: Sorted list
        """
        Z = [list[position] for position in indexes]

        return Z

    def sort_shapely_list_and_chain_list(
        self, cadena_list: List[Chain], shapely_list: List[Ring]
    ) -> Tuple[List[Chain], List[Ring]]:
        """
        Sort shapely list and chain list based on the area of shapely geometries.

        Args:
            cadena_list (List[Chain]): List of chains
            shapely_list (List[Ring]): List of shapely geometries

        Returns:
            Tuple[List, List]: Tuple of sorted chain list and shapely list
        """
        idx_sort = [
            i[0]
            for i in sorted(enumerate(shapely_list), key=lambda x: x[1].geometry.area)
        ]
        cadena_list = self.sort_list_by_index_array(idx_sort, cadena_list)
        shapely_list = self.sort_list_by_index_array(idx_sort, shapely_list)

        return cadena_list, shapely_list

    def _from_completed_chain_to_poly(
        self, completed_chain: List[Chain]
    ) -> Tuple[List[Chain], List[Ring]]:
        """
        Convert completed chains to shapely polygons.

        Args:
            completed_chain (List[Chain]): List of completed chains

        Returns:
            Tuple[List[Chain], List[Ring]]: Tuple of completed chains and shapely polygons
        """
        poly_completed_chains = []

        for chain in completed_chain:
            ring = Ring(chain, id=chain.id)
            poly_completed_chains.append(ring)

        completed_chain, poly_completed_chains = self.sort_shapely_list_and_chain_list(
            completed_chain, poly_completed_chains
        )

        return completed_chain, poly_completed_chains

    def _from_uncompleted_chains_to_poly(
        self, uncompleted_chain: List[Chain]
    ) -> List[LineString]:
        """
        Convert uncompleted chains to shapely LineStrings.

        Args:
            uncompleted_chain (List): List of uncompleted chains

        Returns:
            List[LineString]: List of shapely LineStrings
        """
        uncompleted_chain_shapely = []

        for chain in uncompleted_chain:
            lista_pts = [Point(punto.y, punto.x) for punto in chain.sort_dots()]
            uncompleted_chain_shapely.append(LineString(lista_pts))

        return uncompleted_chain_shapely
