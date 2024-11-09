import numpy as np
from typing import List, Tuple, Optional

from ..geometry.node import Node
from ..geometry.chain import Chain, EndPoints
from ..geometry.geometry_utils import (
    euclidean_distance_between_nodes,
    get_closest_dots_to_angle_on_radial_direction_sorted_by_ascending_distance_to_center,
)


def compute_interpolation_domain(
    endpoint: str, endpoint_cad1: Node, endpoint_cad2: Node, nr: int
) -> List[float]:
    """
    Compute the interpolation domain between two endpoints.

    Args:
        endpoint (str): endpoint type
        endpoint_cad1 (Node): first endpoint
        endpoint_cad2 (Node): second endpoint
        nr (int): number of radial distances

    Returns:
        List[float]: interpolation domain
    """
    interpolation_domain = []

    step = 360 / nr if endpoint == EndPoints.B else -360 / nr
    current_angle = endpoint_cad1.angle

    while current_angle % 360 != endpoint_cad2.angle:
        current_angle += step
        current_angle = current_angle % 360
        interpolation_domain.append(current_angle)

    return interpolation_domain[:-1]


def from_polar_to_cartesian(
    r: float, angulo: float, centro: Tuple[float, float]
) -> Tuple[float, float]:
    """
    Convert polar coordinates to cartesian coordinates.

    Args:
        r (float): radial distance
        angulo (float): angle in degrees
        centro (Tuple[float, float]): center coordinates

    Returns:
        Tuple[float, float]: cartesian coordinates
    """
    y = centro[0] + r * np.cos(angulo * np.pi / 180)
    x = centro[1] + r * np.sin(angulo * np.pi / 180)

    return (y, x)


def generate_node_list_between_two_support_chains_and_two_radial_distances(
    r2_ratio: float,
    r1_ratio: float,
    total_nodes: int,
    interpolation_angle_domain: List[float],
    center: Tuple[float, float],
    inward_chain: Chain,
    outward_chain: Chain,
    chain: Chain,
) -> List[Node]:
    """
    Generate a list of nodes between two support chains and two radial distances.

    Args:
        r2_ratio (float): radial distance of the last node
        r1_ratio (float): radial distance of the first node
        total_nodes (int): total nodes to generate
        interpolation_angle_domain (List[float]): radii angle of the nodes to generate
        center (Tuple[float, float]): center node of the disk
        inward_chain (Chain): inward support chain
        outward_chain (Chain): outward support chain
        chain (Chain): chain to be completed

    Returns:
        List[Node]: generated nodes list
    """
    cad_id = chain.id
    generated_node_list = []
    m = (r2_ratio - r1_ratio) / total_nodes
    n = r1_ratio

    for idx_current_node, angle in enumerate(interpolation_angle_domain):
        dot_list_in_radial_direction = get_closest_dots_to_angle_on_radial_direction_sorted_by_ascending_distance_to_center(
            [inward_chain], angle % 360
        )
        support_node = dot_list_in_radial_direction[0]
        radio_init = support_node.radial_distance
        dot_list_in_radial_direction = get_closest_dots_to_angle_on_radial_direction_sorted_by_ascending_distance_to_center(
            [outward_chain], angle % 360
        )
        support_node = dot_list_in_radial_direction[0]
        radio_superior = support_node.radial_distance
        radial_distance_between_chains = radio_superior - radio_init

        radio_inter = (
            m * (idx_current_node) + n
        ) * radial_distance_between_chains + radio_init
        i, j = from_polar_to_cartesian(radio_inter, angle % 360, center)
        i = i if i < chain.img_height else chain.img_height - 1
        j = j if j < chain.img_width else chain.img_width - 1

        # radios.append(radio_inter)
        params = {
            "x": j,
            "y": i,
            "angle": angle % 360,
            "radial_distance": radio_inter,
            "chain_id": cad_id,
        }

        node = Node(**params)
        generated_node_list.append(node)

    return generated_node_list


def generate_nodes_list_between_two_radial_distances(
    r2: float,
    r1: float,
    total_nodes: int,
    interpolation_angular_domain: List[float],
    center: Tuple[float, float],
    sign: int,
    ch_i: Optional[Chain],
    ch_j: Chain,
) -> List[Node]:
    """
    Generate a list of nodes between two radial distances.

    Args:
        r2 (float): radial distance of the last node
        r1 (float): radial distance of the first node
        total_nodes (int): total nodes to generate
        interpolation_angular_domain (List[float]): radii angle of the nodes to generate
        center (Tuple[float, float]): center node of the disk
        sign (int): sign of the radial distance
        ch_i (Optional[Chain]): inward support chain
        ch_j (Chain): outward support chain

    Returns:
        List[Node]: generated nodes list
    """
    cad_id = ch_j.id
    l_generated_node = []
    m = (r2 - r1) / (total_nodes - 0)
    n = r1 - m * 0
    for current_idx_node, angle in enumerate(interpolation_angular_domain):
        if ch_i is not None:
            dot_list_in_radial_direction = get_closest_dots_to_angle_on_radial_direction_sorted_by_ascending_distance_to_center(
                [ch_i], angle % 360
            )

            support_node = dot_list_in_radial_direction[0]
            radio_init = support_node.radial_distance
            # radio_init = r1
        else:
            radio_init = 0

        radio_inter = sign * (m * (current_idx_node) + n) + radio_init
        i, j = from_polar_to_cartesian(radio_inter, angle % 360, center)
        i = i if i < ch_j.img_height else ch_j.img_height - 1
        j = j if j < ch_j.img_width else ch_j.img_width - 1

        l_generated_node.append(
            Node(
                **{
                    "x": j,
                    "y": i,
                    "angle": angle % 360,
                    "radial_distance": radio_inter,
                    "chain_id": cad_id,
                }
            )
        )

    return l_generated_node


def get_radial_distance_to_chain(chain: Chain, dot: Node) -> float:
    """
    Get the radial distance to a chain.

    Args:
        chain (Chain): chain to compute the radial distance
        dot (Node): node to compute the radial distance

    Returns:
        float: radial distance
    """
    dot_list_in_radial_direction = get_closest_dots_to_angle_on_radial_direction_sorted_by_ascending_distance_to_center(
        [chain], dot.angle
    )
    soporte_pto1 = dot_list_in_radial_direction[0]
    rii = euclidean_distance_between_nodes(soporte_pto1, dot)

    return rii


def compute_radial_ratio(
    cadena_inferior: Chain, cadena_superior: Chain, dot: Node
) -> float:
    """
    Compute the radial ratio between two chains.

    Args:
        cadena_inferior (Chain): inferior chain
        cadena_superior (Chain): superior chain
        dot (Node): node to compute the radial distance

    Returns:
        float: radial ratio
    """
    r1_inferior = get_radial_distance_to_chain(cadena_inferior, dot)
    r1_superior = get_radial_distance_to_chain(cadena_superior, dot)

    return r1_inferior / (r1_superior + r1_inferior)


def interpolate_in_angular_domain_via_2_chains(
    inward_support_chain: Chain,
    outward_support_chain: Chain,
    ch1_endpoint: Node,
    ch2_endpoint: Node,
    endpoint: str,
    ch1: Chain,
    node_list: List[Node],
) -> None:
    """
    Interpolate in the angular domain using two chains.

    Args:
        inward_support_chain (Chain): inward support chain
        outward_support_chain (Chain): outward support chain
        ch1_endpoint (Node): chain 1 endpoint
        ch2_endpoint (Node): chain 2 endpoint
        endpoint (str): endpoint type
        ch1 (Chain): chain 1
        node_list (List[Node]): list of nodes

    Returns:
        None
    """
    # 1. Domain angle interpolation
    domain_angle_interpolation = compute_interpolation_domain(
        endpoint, ch1_endpoint, ch2_endpoint, ch1.nr
    )
    center = ch1.center

    # 2. Compute radial ratio
    r1_ratio = compute_radial_ratio(
        inward_support_chain, outward_support_chain, ch1_endpoint
    )
    r2_ratio = compute_radial_ratio(
        inward_support_chain, outward_support_chain, ch2_endpoint
    )

    # 3. Generate nodes
    total_nodes = len(domain_angle_interpolation)
    if total_nodes == 0:
        return

    generated_nodes = (
        generate_node_list_between_two_support_chains_and_two_radial_distances(
            r2_ratio,
            r1_ratio,
            total_nodes,
            domain_angle_interpolation,
            center,
            inward_support_chain,
            outward_support_chain,
            ch1,
        )
    )

    node_list += generated_nodes

    return


def domain_interpolation(
    ch_i: Optional[Chain],
    ch_j_endpoint: Node,
    ch_k_endpoint: Node,
    endpoint: int,
    ch_j: Chain,
    l_nodes: List[Node],
) -> None:
    """
    Interpolate between endpoint ch_j_endpoint and ch_k_endpoint using ch_i as support ch_j. Ch_j is the source ch_j to
    be connected

    Args:
        ch_i (Optional[Chain]): support ch_i
        ch_j_endpoint (Node): ch_j endpoint
        ch_k_endpoint (Node): ch_k endpoint
        endpoint (int): endpoint type
        ch_j (Chain): ch_j to be connected
        l_nodes (List[Node]): list of nodes

    Returns:
        None
    """
    domain_angles = compute_interpolation_domain(
        endpoint, ch_j_endpoint, ch_k_endpoint, ch_j.nr
    )
    center = ch_j.center

    if ch_i is not None:
        dot_list_in_radial_direction = get_closest_dots_to_angle_on_radial_direction_sorted_by_ascending_distance_to_center(
            [ch_i], ch_j_endpoint.angle
        )
        node1_support = dot_list_in_radial_direction[0]
        r1 = euclidean_distance_between_nodes(node1_support, ch_j_endpoint)
        dot_list_in_radial_direction = get_closest_dots_to_angle_on_radial_direction_sorted_by_ascending_distance_to_center(
            [ch_i], ch_k_endpoint.angle
        )
        node2_support = dot_list_in_radial_direction[0]
        sign = (
            -1 if node2_support.radial_distance > ch_k_endpoint.radial_distance else +1
        )
        r2 = euclidean_distance_between_nodes(node2_support, ch_k_endpoint)
    else:
        r1 = ch_j_endpoint.radial_distance
        r2 = ch_k_endpoint.radial_distance
        sign = 1

    total_nodes = len(domain_angles)
    if total_nodes == 0:
        return

    l_generated_nodes = generate_nodes_list_between_two_radial_distances(
        r2, r1, total_nodes, domain_angles, center, sign, ch_i, ch_j
    )

    l_nodes += l_generated_nodes

    return


def complete_chain_using_2_support_ring(
    inward_chain: Chain, outward_chain: Chain, chain: Chain
) -> bool:
    """
    Complete ch_i using two support rings

    Args:
        inward_chain (Chain): inward chain
        outward_chain (Chain): outward chain
        chain (Chain): chain to be completed

    Returns:
        bool: boolean value indicating if the border has changed
    """
    ch1_endpoint = chain.extB
    ch2_endpoint = chain.extA
    endpoint = EndPoints.B
    generated_nodes = []

    interpolate_in_angular_domain_via_2_chains(
        inward_chain,
        outward_chain,
        ch1_endpoint,
        ch2_endpoint,
        endpoint,
        chain,
        generated_nodes,
    )

    change_border = chain.add_nodes_list(generated_nodes)

    return change_border


def complete_chain_using_support_ring(support_chain: Chain, ch1: Chain) -> bool:
    """
    Complete ch_i using a support ring

    Args:
        support_chain (Chain): support chain
        ch1 (Chain): chain to be completed

    Returns:
        bool: boolean value indicating if the border has changed
    """
    ch1_endpoint = ch1.extB
    ch2_endpoint = ch1.extA
    endpoint = EndPoints.B
    generated_list_nodes = []
    domain_interpolation(
        support_chain, ch1_endpoint, ch2_endpoint, endpoint, ch1, generated_list_nodes
    )
    change_border = ch1.add_nodes_list(generated_list_nodes)

    return change_border


def connect_2_chain_via_inward_and_outward_ring(
    outward_chain: Chain,
    inward_chain: Chain,
    chain1: Chain,
    chain2: Chain,
    node_list: List[Node],
    endpoint: int,
) -> Tuple[List[Node], bool]:
    """
    Connect 2 ch_i via inward and outward ring

    Args:
        outward_chain (Chain): outward chain
        inward_chain (Chain): inward chain
        chain1 (Chain): chain 1
        chain2 (Chain): chain 2
        node_list (List[Node]): list of nodes
        endpoint (int): endpoint type

    Returns:
        Tuple[List[Node], bool]: generated nodes list and boolean value indicating if the border has changed
    """
    ch1_endpoint = chain1.extA if endpoint == EndPoints.A else chain1.extB
    ch2_endpoint = chain2.extB if endpoint == EndPoints.A else chain2.extA

    # 1.0
    generated_node_list = []
    interpolate_in_angular_domain_via_2_chains(
        inward_chain,
        outward_chain,
        ch1_endpoint,
        ch2_endpoint,
        endpoint,
        chain1,
        generated_node_list,
    )
    node_list += generated_node_list

    # 2.0
    chain_2_nodes = []
    chain_2_nodes += chain2.l_nodes
    for node in chain_2_nodes:
        node.chain_id = chain1.id

    change_border = chain1.add_nodes_list(chain_2_nodes + generated_node_list)

    return generated_node_list, change_border
