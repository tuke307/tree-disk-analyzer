from typing import Any, List, Optional, Tuple
import cv2
import matplotlib.pyplot as plt
import numpy as np

from ..geometry.virtual_band_generator import VirtualBandGenerator
from ..analysis.chain_neighbourhood import ChainNeighbourhood
from ..geometry.node import Node
from ..geometry.chain import Chain, EndPoints
from ..geometry.geometry_utils import (
    get_node_from_list_by_angle,
    visualize_selected_ch_and_chains_over_image_,
)
from ..analysis.interpolation_nodes import (
    domain_interpolation,
)


def draw_segment_between_nodes(
    pto1: Node,
    pto2: Node,
    img: np.ndarray,
    color: Tuple[int, int, int] = (0, 255, 0),
    thickness: int = 2,
) -> np.ndarray:
    """
    Draws a segment between two nodes on an image.

    Args:
        pto1 (Node): First point.
        pto2 (Node): Second point.
        img (np.ndarray): Image to draw on.
        color (Tuple[int, int, int]): Color of the line.
        thickness (int): Thickness of the line.

    Returns:
        np.ndarray: Image with the drawn segment.
    """
    pts = np.ndarray([[pto1.y, pto1.x], [pto2.y, pto2.x]], dtype=int)
    isClosed = False
    img = cv2.polylines(img, [pts], isClosed, color, thickness)

    return img


def vector_derivative(f: np.ndarray, nr: int) -> np.ndarray:
    """
    Computes the central derivative of a vector.

    Args:
        f (np.ndarray): Input vector.
        nr (int): Number of rays (unused).

    Returns:
        np.ndarray: Derivative of the vector.
    """
    return np.gradient(f)


def regularity_of_the_derivative_condition(
    state: Any,
    nr: int,
    ch_jk_nodes: List[Node],
    ch_j_nodes: List[Node],
    ch_k_nodes: List[Node],
    endpoint_j: EndPoints,
    th_deriv: float = 1.0,
) -> bool:
    """
    Computes the regularity of the derivative condition.

    Args:
        state (Any): State object for debugging purposes.
        nr (int): Number of rays.
        ch_jk_nodes (List[Node]): Nodes of the combined chains.
        ch_j_nodes (List[Node]): Nodes of the source chain.
        ch_k_nodes (List[Node]): Nodes of the destination chain.
        endpoint_j (EndPoints): Endpoint of the source chain.
        th_deriv (float): Derivative threshold.

    Returns:
        bool: True if the derivative is regular, False otherwise.
    """
    ch_jk_radials = [node.radial_distance for node in ch_jk_nodes]
    nodes_radial_distance_src_chain = [node.radial_distance for node in ch_j_nodes]
    nodes_radial_distance_dst_chain = [node.radial_distance for node in ch_k_nodes]

    abs_der_1 = np.abs(vector_derivative(nodes_radial_distance_src_chain, nr))
    abs_der_2 = np.abs(vector_derivative(nodes_radial_distance_dst_chain, nr))
    abs_der_3 = np.abs(vector_derivative(ch_jk_radials, nr))
    maximum_derivative_chains = np.maximum(abs_der_1.max(), abs_der_2.max())

    max_derivative_end = np.max(abs_der_3)
    RegularDeriv = max_derivative_end <= maximum_derivative_chains * th_deriv

    if state is not None and getattr(state, "debug", False):
        f, (ax2, ax1) = plt.subplots(2, 1)
        ax1.plot(abs_der_3)
        if endpoint_j == EndPoints.A:
            ax1.plot(np.arange(0, len(abs_der_2)), abs_der_2[::-1])
            ax1.plot(
                np.arange(
                    len(ch_jk_radials) - len(nodes_radial_distance_src_chain),
                    len(ch_jk_radials),
                ),
                abs_der_1,
            )
        else:
            ax1.plot(np.arange(0, len(abs_der_1)), abs_der_1[::-1])
            ax1.plot(
                np.arange(
                    len(ch_jk_radials) - len(nodes_radial_distance_dst_chain),
                    len(ch_jk_radials),
                ),
                abs_der_2,
            )

        ax1.hlines(
            y=max_derivative_end,
            xmin=0,
            xmax=np.maximum(
                len(nodes_radial_distance_src_chain),
                len(nodes_radial_distance_dst_chain),
            ),
            label="Salto",
        )
        ax1.hlines(
            y=th_deriv * maximum_derivative_chains,
            xmin=0,
            xmax=np.maximum(
                len(nodes_radial_distance_dst_chain),
                len(nodes_radial_distance_src_chain),
            ),
            colors="r",
            label="umbral",
        )
        ax1.legend()

        ax2.plot(ch_jk_radials)
        if endpoint_j == EndPoints.A:
            ax2.plot(
                np.arange(0, len(abs_der_2)), nodes_radial_distance_dst_chain[::-1], "r"
            )
            ax2.plot(
                np.arange(
                    len(ch_jk_radials) - len(nodes_radial_distance_src_chain),
                    len(ch_jk_radials),
                ),
                nodes_radial_distance_src_chain,
            )
        else:
            ax2.plot(
                np.arange(0, len(abs_der_1)), nodes_radial_distance_src_chain[::-1], "r"
            )
            ax2.plot(
                np.arange(
                    len(ch_jk_radials) - len(nodes_radial_distance_dst_chain),
                    len(ch_jk_radials),
                ),
                nodes_radial_distance_dst_chain,
            )

        plt.title(f"{RegularDeriv}")
        plt.savefig(f"{str(state.path)}/{state.counter}_derivada_{RegularDeriv}.png")
        plt.close()
        state.counter += 1

    return RegularDeriv


def generate_virtual_nodes_without_support_chain(
    ch_1: Chain, ch_2: Chain, endpoint: EndPoints
) -> List[Node]:
    """
    Generates virtual nodes between two chains without a support chain.

    Args:
        ch_1 (Chain): First chain.
        ch_2 (Chain): Second chain.
        endpoint (EndPoints): Endpoint to connect.

    Returns:
        List[Node]: List of virtual nodes.
    """
    ch1_border = ch_1.extA if endpoint == EndPoints.A else ch_1.extB
    ch2_border = ch_2.extB if endpoint == EndPoints.A else ch_2.extA

    virtual_nodes = []
    support_chain = None
    domain_interpolation(
        support_chain, ch1_border, ch2_border, endpoint, ch_1, virtual_nodes
    )

    return virtual_nodes


def regularity_of_the_derivative(
    state: Any,
    ch_j: Chain,
    ch_k: Chain,
    endpoint_j: EndPoints,
    node_list: List[Node],
    ch_j_nodes: List[Node],
    ch_k_nodes: List[Node],
    th_deriv: float = 1.0,
    derivative_from_center: bool = False,
) -> bool:
    """
    Checks the regularity of the derivative for the virtual nodes generated between two chains.

    Args:
        state (Any): State object for debugging purposes.
        ch_j (Chain): Source chain to be connected.
        ch_k (Chain): Destination chain to be connected.
        endpoint_j (EndPoints): Endpoint of ch_j to be connected.
        node_list (List[Node]): All the nodes involved in the connection, including the virtual nodes.
        ch_j_nodes (List[Node]): Nodes of ch_j.
        ch_k_nodes (List[Node]): Nodes of ch_k.
        th_deriv (float): Derivative threshold.
        derivative_from_center (bool): If True, regenerate virtual nodes interpolating from the center of ch_i.

    Returns:
        bool: True if the derivative is regular, False otherwise.
    """
    if derivative_from_center:
        new_list = []
        virtual_nodes = generate_virtual_nodes_without_support_chain(
            ch_j, ch_k, endpoint_j
        )
        angles = [n.angle for n in virtual_nodes]
        for node in node_list:
            if node.angle not in angles:
                new_list.append(node)
            else:
                new_list.append(get_node_from_list_by_angle(virtual_nodes, node.angle))
        node_list = new_list

    RegularDeriv = regularity_of_the_derivative_condition(
        state, ch_j.nr, node_list, ch_j_nodes, ch_k_nodes, endpoint_j, th_deriv=th_deriv
    )

    return RegularDeriv


def radial_tolerance_for_connecting_chains(
    state: Any, th_radial_tolerance: float, endpoints_radial: List[float]
) -> bool:
    """
    Checks maximum radial distance allowed to connect chains.

    Args:
        state (Any): State object for debugging purposes.
        th_radial_tolerance (float): Radial tolerance threshold.
        endpoints_radial (List[float]): Radial distances between endpoints and support chain.

    Returns:
        bool: True if radial distance is within tolerance, False otherwise.
    """
    delta_ri = endpoints_radial[0]
    delta_ri_plus_i = endpoints_radial[1]
    inf_delta_ri = delta_ri * (1 - th_radial_tolerance)
    sup_delta_ri = delta_ri * (1 + th_radial_tolerance)
    RadialTol = inf_delta_ri <= delta_ri_plus_i <= sup_delta_ri

    if state is not None and getattr(state, "debug", False):
        plt.figure()
        plt.axvline(x=delta_ri, color="b", label="delta_ri")
        plt.axvline(x=delta_ri_plus_i, color="r", label="delta_ri_plus_i")
        plt.axvline(x=inf_delta_ri, color="k", label="inf radial")
        plt.axvline(x=sup_delta_ri, color="k", label="sup radial")
        plt.title(f"{RadialTol}: Th {th_radial_tolerance}.")
        plt.savefig(f"{str(state.path)}/{state.counter}_max_radial_condition.png")
        plt.close()
        state.counter += 1

    return RadialTol


def similar_radial_distances_of_nodes_in_both_chains(
    state: Any, distribution_th: float, set_j: List[float], set_k: List[float]
) -> Tuple[bool, float]:
    """
    Checks if the radial distances of the nodes in both chains are similar via distribution of the radial distances.

    Args:
        state (Any): State object for debugging purposes.
        distribution_th (float): Size of the distributions to check if they are similar.
        set_j (List[float]): Radial distances between nodes of the first chain and the support chain.
        set_k (List[float]): Radial distances between nodes of the second chain and the support chain.

    Returns:
        Tuple[bool, float]: (Similarity result, distance between the mean of the distributions).
    """
    mean_j = np.mean(set_j)
    sigma_j = np.std(set_j)
    inf_range_j = mean_j - distribution_th * sigma_j
    sup_range_j = mean_j + distribution_th * sigma_j

    mean_k = np.mean(set_k)
    std_k = np.std(set_k)
    inf_range_k = mean_k - distribution_th * std_k
    sup_range_k = mean_k + distribution_th * std_k

    SimilarRadialDist = inf_range_k <= sup_range_j and inf_range_j <= sup_range_k

    if state is not None and getattr(state, "debug", False):
        plt.figure()
        plt.hist(set_j, bins=10, alpha=0.3, color="r", label="src radial")
        plt.hist(set_k, bins=10, alpha=0.3, color="b", label="dst radial")
        plt.axvline(x=inf_range_j, color="r", label="inf src")
        plt.axvline(x=sup_range_j, color="r", label="sup src")
        plt.axvline(x=inf_range_k, color="b", label="inf dst")
        plt.axvline(x=sup_range_k, color="b", label="sup dst")
        plt.legend()
        plt.title(f"{SimilarRadialDist}: Th {distribution_th}.")
        plt.savefig(f"{str(state.path)}/{state.counter}_distribution_condition.png")
        plt.close()
        state.counter += 1

    return SimilarRadialDist, np.abs(mean_j - mean_k)


def similarity_conditions(
    state: Any,
    th_radial_tolerance: float,
    th_distribution_size: float,
    th_regular_derivative: float,
    derivative_from_center: bool,
    ch_i: Chain,
    ch_j: Chain,
    candidate_chain: Chain,
    endpoint: EndPoints,
    check_overlapping: bool = True,
    chain_list: Optional[List[Chain]] = None,
) -> Tuple[bool, float]:
    """
    Checks the similarity conditions defined in Equation 6 in the paper.

    Args:
        state (Any): State object for debugging purposes.
        th_radial_tolerance (float): Radial tolerance threshold.
        th_distribution_size (float): Distribution size threshold.
        th_regular_derivative (float): Regular derivative threshold.
        derivative_from_center (bool): If True, regenerate virtual nodes from the center.
        ch_i (Chain): Support chain.
        ch_j (Chain): Chain j to connect.
        candidate_chain (Chain): Candidate chain to connect.
        endpoint (EndPoints): Endpoint of the source chain.
        check_overlapping (bool): Whether to check for overlapping chains.
        chain_list (Optional[List[Chain]]): List of chains to check for overlapping.

    Returns:
        Tuple[bool, float]: (Similarity condition result, distance between radial distributions).
    """
    neighbourhood = ChainNeighbourhood(ch_j, candidate_chain, ch_i, endpoint)

    if state is not None and getattr(state, "debug", False):
        visualize_selected_ch_and_chains_over_image_(
            [ch_i, ch_j, candidate_chain],
            state.l_ch_s,
            img=state.img,
            filename=f"{state.path}/{state.counter}_radial_conditions_{endpoint}.png",
        )
        state.counter += 1
        neighbourhood.draw_neighbourhood(
            f"{state.path}/{state.counter}_radials_conditions_neighbourdhood_{ch_j.label_id}_{candidate_chain.label_id}.png"
        )
        state.counter += 1

    if len(neighbourhood.set_i) <= 1 or len(neighbourhood.set_k) <= 1:
        return False, -1

    # 1. Radial tolerance for connecting chains
    RadialTol = radial_tolerance_for_connecting_chains(
        state, th_radial_tolerance, neighbourhood.radial_distance_endpoints_to_support
    )

    # 2. Similar radial distances of nodes in both chains
    SimilarRadialDist, distribution_distance = (
        similar_radial_distances_of_nodes_in_both_chains(
            state, th_distribution_size, neighbourhood.set_i, neighbourhood.set_k
        )
    )

    check_pass = RadialTol or SimilarRadialDist
    if not check_pass:
        return False, distribution_distance

    # 3. Derivative condition
    RegularDeriv = regularity_of_the_derivative(
        state,
        ch_j,
        candidate_chain,
        endpoint,
        neighbourhood.neighbourhood_nodes,
        ch_j_nodes=neighbourhood.src_chain_nodes,
        ch_k_nodes=neighbourhood.dst_chain_nodes,
        th_deriv=th_regular_derivative,
        derivative_from_center=derivative_from_center,
    )

    if not RegularDeriv:
        return False, distribution_distance

    # 4.0 Check there is no chains in region
    if check_overlapping:
        exist_chain = exist_chain_overlapping(
            state.l_ch_s if chain_list is None else chain_list,
            neighbourhood.endpoint_and_virtual_nodes,
            ch_j,
            candidate_chain,
            endpoint,
            ch_i,
        )
        if exist_chain:
            return False, distribution_distance

    return True, distribution_distance


def exist_chain_in_band_logic(
    chain_list: List[Chain], band_info: VirtualBandGenerator
) -> List[Chain]:
    """
    Checks for chains within the band.

    Args:
        chain_list (List[Chain]): List of chains to check.
        band_info (InfoVirtualBand): Band information.

    Returns:
        List[Chain]: List of chains found in the band.
    """
    chain_of_interest = [band_info.ch_k, band_info.ch_j]
    if band_info.ch_i is not None:
        chain_of_interest.append(band_info.ch_i)

    fist_chain_in_region = next(
        (
            chain
            for chain in chain_list
            if chain not in chain_of_interest and band_info.is_chain_in_band(chain)
        ),
        None,
    )

    return [fist_chain_in_region] if fist_chain_in_region is not None else []


def exist_chain_overlapping(
    l_ch_s: List[Chain],
    l_nodes: List[Node],
    ch_j: Chain,
    ch_k: Chain,
    endpoint_type: EndPoints,
    ch_i: Chain,
) -> bool:
    """
    Checks if there is a chain in the area within the band.

    Algorithm 11 in the supplementary material.

    Args:
        l_ch_s (List[Chain]): Full chains list.
        l_nodes (List[Node]): Both endpoints and virtual nodes.
        ch_j (Chain): Source chain.
        ch_k (Chain): Destination chain.
        endpoint_type (EndPoints): Endpoint type of ch_j.
        ch_i (Chain): Support chain.

    Returns:
        bool: True if a chain exists in the band, False otherwise.
    """
    info_band = VirtualBandGenerator(l_nodes, ch_j, ch_k, endpoint_type, ch_i)
    l_chains_in_band = exist_chain_in_band_logic(l_ch_s, info_band)
    exist_chain = len(l_chains_in_band) > 0

    return exist_chain
