from enum import Enum
from typing import List, Optional, Tuple, Any

import matplotlib.pyplot as plt
import numpy as np

from ..visualization.drawing import Drawing
from ..geometry.node import Node
from ..geometry.curve import Curve
from ..geometry.chain import Chain, TypeChains, EndPoints


def euclidean_distance(pix1: np.array, pix2: np.array) -> float:
    """
    Calculates the Euclidean distance between two pixels.

    Args:
        pix1 (np.array): Coordinates of the first pixel.
        pix2 (np.array): Coordinates of the second pixel.

    Returns:
        float: Euclidean distance between pix1 and pix2.
    """
    return np.sqrt((pix1[0] - pix2[0]) ** 2 + (pix1[1] - pix2[1]) ** 2)


def get_node_from_list_by_angle(dot_list: List[Node], angle: float) -> Optional[Node]:
    """
    Retrieves a node from a list by its angle.

    Args:
        dot_list (List[Node]): List of nodes to search.
        angle (float): Angle to match.

    Returns:
        Optional[Node]: The node with the specified angle, or None if not found.
    """
    try:
        dot = next(dot for dot in dot_list if (dot.angle == angle))
    except StopIteration:
        dot = None
    return dot


def get_chain_from_list_by_id(
    chain_list: List[Chain], chain_id: int
) -> Optional[Chain]:
    """
    Retrieves a chain from a list by its ID.

    Args:
        chain_list (List[Chain]): List of chains to search.
        chain_id (int): ID of the chain to find.

    Returns:
        Optional[Chain]: The chain with the specified ID, or None if not found.
    """
    try:
        chain_in_list = next(chain for chain in chain_list if (chain.id == chain_id))
    except StopIteration:
        chain_in_list = None

    return chain_in_list


def euclidean_distance_between_nodes(d1: Node, d2: Node) -> float:
    """
    Computes Euclidean distance between two nodes.

    Args:
        d1 (Node): First node.
        d2 (Node): Second node.

    Returns:
        float: Euclidean distance between the two nodes.
    """
    v1 = np.array([d1.x, d1.y], dtype=float)
    v2 = np.array([d2.x, d2.y], dtype=float)

    return euclidean_distance(v1, v2)


def copy_node(node: Node) -> Node:
    """
    Creates a copy of a node.

    Args:
        node (Node): Node to copy.

    Returns:
        Node: A new node with the same attributes as the original.
    """
    return Node(
        x=node.x,
        y=node.y,
        chain_id=node.chain_id,
        radial_distance=node.radial_distance,
        angle=node.angle,
    )


def copy_chain(chain: Chain) -> Chain:
    """
    Creates a copy of a chain.

    Args:
        chain (Chain): Chain to copy.

    Returns:
        Chain: A new chain with copied nodes.
    """
    aux_chain = Chain(
        chain.id,
        chain.nr,
        chain.center,
        chain.img_height,
        chain.img_width,
        type=chain.type,
    )
    aux_chain_node_list = [copy_node(node) for node in chain.l_nodes]
    aux_chain.add_nodes_list(aux_chain_node_list)
    return aux_chain


def angular_distance_between_endpoints(endpoint_j: Node, endpoint_k: Node) -> float:
    """
    Compute angular distance between endpoints.

    Args:
        endpoint_j (Node): Endpoint node j of chain ch_j.
        endpoint_k (Node): Endpoint node k of chain ch_k.

    Returns:
        float: Angular distance in degrees.
    """
    cte_degrees_in_a_circle = 360
    angular_distance = (
        endpoint_j.angle - endpoint_k.angle + cte_degrees_in_a_circle
    ) % cte_degrees_in_a_circle
    return angular_distance


def angular_distance_between_chains(
    ch_j: Chain, ch_k: Chain, endpoint_j_type: EndPoints
) -> float:
    """
    Compute angular distance between chains' endpoints.

    If endpoint_j == A then compute distance between chain.extA and ch_k.extB.
    Otherwise, compute distance between chain.extB and ch_k.extA.

    Args:
        ch_j (Chain): Chain j.
        ch_k (Chain): Chain k.
        endpoint_j_type (EndPoints): Endpoint type of chain j (A or B).

    Returns:
        float: Angular distance between endpoints in degrees.
    """
    endpoint_k = ch_k.extB if endpoint_j_type == EndPoints.A else ch_k.extA
    endpoint_j = ch_j.extA if endpoint_j_type == EndPoints.A else ch_j.extB

    angular_distance = (
        angular_distance_between_endpoints(endpoint_k, endpoint_j)
        if endpoint_j_type == EndPoints.B
        else angular_distance_between_endpoints(endpoint_j, endpoint_k)
    )

    return angular_distance


def minimum_euclidean_distance_between_vector_and_matrix(
    vector: np.array, matrix: np.array
) -> float:
    """
    Compute minimum Euclidean distance between a vector and each row in a matrix.

    Args:
        vector (np.array): Vector.
        matrix (np.array): Matrix.

    Returns:
        float: Minimum distance.
    """
    distances = np.sqrt(np.sum((matrix - vector) ** 2, axis=1))

    return np.min(distances)


def minimum_euclidean_distance_between_chains_endpoints(
    ch_j: Chain, ch_k: Chain
) -> float:
    """
    Compute minimum Euclidean distance between ch_j and ch_k endpoints.

    Args:
        ch_j (Chain): Chain j.
        ch_k (Chain): Chain k.

    Returns:
        float: Minimum Euclidean distance between endpoints.
    """
    nodes1, c1a, c1b = ch_j.to_array()
    nodes2, c2a, c2b = ch_k.to_array()
    c2a_min = minimum_euclidean_distance_between_vector_and_matrix(c2a, nodes1)
    c2b_min = minimum_euclidean_distance_between_vector_and_matrix(c2b, nodes1)
    c1a_min = minimum_euclidean_distance_between_vector_and_matrix(c1a, nodes2)
    c1b_min = minimum_euclidean_distance_between_vector_and_matrix(c1b, nodes2)
    return np.min([c2a_min, c2b_min, c1a_min, c1b_min])


def get_chains_within_angle(angle: float, chain_list: List[Chain]) -> List[Chain]:
    """
    Get chains that cover a specific angle.

    Args:
        angle (float): Angle in degrees.
        chain_list (List[Chain]): List of chains.

    Returns:
        List[Chain]: List of chains that cover the angle.
    """
    chains_list = []
    for chain in chain_list:
        A = chain.extA.angle
        B = chain.extB.angle
        if (A <= B and A <= angle <= B) or (A > B and (A <= angle or angle <= B)):
            chains_list.append(chain)
    return chains_list


def get_closest_chain_border_to_angle(chain: Chain, angle: float) -> Node:
    """
    Get the closest endpoint of a chain to a given angle.

    Args:
        chain (Chain): Chain to search.
        angle (float): Angle in degrees.

    Returns:
        Node: Closest endpoint node.
    """
    B = chain.extB.angle
    A = chain.extA.angle
    if B < A:
        dist_to_b = 360 - angle + B if angle > B else B - angle
        dist_to_a = angle - A if angle > B else 360 - A + angle
    else:
        dist_to_a = A - angle
        dist_to_b = angle - B
    # assert dist_to_a > 0 and dist_to_b > 0
    dot = chain.extB if dist_to_b < dist_to_a else chain.extA
    return dot


def get_closest_dots_to_angle_on_radial_direction_sorted_by_ascending_distance_to_center(
    chains_list: List[Chain], angle: float
) -> List[Node]:
    """
    Get nodes of all chains that are over the ray defined by angle and sort them by ascending distance to center.

    Args:
        chains_list (List[Chain]): List of chains.
        angle (float): Ray angle direction.

    Returns:
        List[Node]: Nodes sorted by ascending distance to center over ray direction angle.
    """
    node_list_over_ray = []
    for chain in chains_list:
        try:
            node = next(node for node in chain.l_nodes if node.angle == angle)
        except StopIteration:
            node = get_closest_chain_border_to_angle(chain, angle)

        if node not in node_list_over_ray:
            node_list_over_ray.append(node)

    if node_list_over_ray:
        node_list_over_ray.sort(key=lambda x: x.radial_distance)

    return node_list_over_ray


def get_nodes_from_chain_list(chain_list: List[Chain]) -> List[Node]:
    """
    Retrieves all nodes from a list of chains.

    Args:
        chain_list (List[Chain]): List of chains.

    Returns:
        List[Node]: List of all nodes in the chains.
    """
    inner_nodes = []
    for chain in chain_list:
        inner_nodes.extend(chain.l_nodes)
    return inner_nodes


def get_nodes_angles_from_list_nodes(node_list: List[Node]) -> List[float]:
    """
    Retrieves angles from a list of nodes.

    Args:
        node_list (List[Node]): List of nodes.

    Returns:
        List[float]: List of node angles.
    """
    return [node.angle for node in node_list]


def visualize_chains_over_image(
    chain_list: List[Chain] = [],
    img: Optional[np.ndarray] = None,
    filename: Optional[str] = None,
    devernay: Optional[np.ndarray] = None,
    filter: Optional[np.ndarray] = None,
) -> None:
    """
    Visualizes chains over an image.

    Args:
        chain_list (List[Chain]): List of chains to visualize.
        img (Optional[np.ndarray]): Image to display chains over.
        filename (Optional[str]): Filename to save the image.
        devernay (Optional[np.ndarray]): Devernay curves.
        filter (Optional[np.ndarray]): Filtered curves.

    Returns:
        None
    """
    if devernay is not None:
        img = Drawing.write_curves_to_image(devernay, img)
    elif filter is not None:
        img = write_filter_curves_to_image(filter, img)

    figsize = (10, 10)
    plt.figure(figsize=figsize)
    plt.imshow(img, cmap="gray")

    for chain in chain_list:
        x, y = chain.get_nodes_coordinates()
        if chain.type == TypeChains.normal:
            if chain.is_closed():
                x = x.tolist() + [x[0]]
                y = y.tolist() + [y[0]]
                plt.plot(x, y, "b", linewidth=1)
            else:
                plt.plot(x, y, "r", linewidth=1)
        elif chain.type == TypeChains.border:
            plt.plot(x, y, "k", linewidth=1)
        else:
            plt.scatter(int(x[0]), int(y[0]), c="k")

    plt.tight_layout()
    plt.axis("off")

    if filename:
        plt.savefig(filename)
    else:
        plt.show()

    plt.close()


def visualize_selected_ch_and_chains_over_image_(
    selected_ch: List[Chain] = [],
    chain_list: List[Chain] = [],
    img: Optional[np.ndarray] = None,
    filename: Optional[str] = None,
    devernay: Optional[np.ndarray] = None,
    filter: Optional[np.ndarray] = None,
) -> None:
    """
    Visualizes selected chains and chain list over an image.

    Args:
        selected_ch (List[Chain]): List of selected chains to highlight.
        chain_list (List[Chain]): List of chains to visualize.
        img (Optional[np.ndarray]): Image to display chains over.
        filename (Optional[str]): Filename to save the image.
        devernay (Optional[np.ndarray]): Devernay curves.
        filter (Optional[np.ndarray]): Filtered curves.

    Returns:
        None
    """
    if devernay is not None:
        img = Drawing.write_curves_to_image(devernay, img)
    elif filter is not None:
        img = write_filter_curves_to_image(filter, img)

    figsize = (10, 10)
    plt.figure(figsize=figsize)
    plt.imshow(img, cmap="gray")
    for chain in chain_list:
        x, y = chain.get_nodes_coordinates()
        plt.plot(x, y, "w", linewidth=3)

    # draw selected chains
    for ch in selected_ch:
        x, y = ch.get_nodes_coordinates()
        plt.plot(x, y, linewidth=3)
        plt.annotate(str(ch.label_id), (x[0], y[0]), c="b")

    plt.tight_layout()
    plt.axis("off")
    if filename:
        plt.savefig(filename)
    plt.close()


def write_filter_curves_to_image(curves: List[Curve], img: np.ndarray) -> np.ndarray:
    """
    Draws filtered curves onto an image.

    Args:
        curves (List[Curve]): List of filtered curves.
        img (np.ndarray): Image to draw on.

    Returns:
        np.ndarray: Image with curves drawn.
    """
    img = np.full_like(img, 255)

    for c in curves:
        img = c.draw(img, thickness=3)

    return img
