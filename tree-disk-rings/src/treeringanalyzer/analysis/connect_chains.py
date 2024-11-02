import numpy as np
from typing import List, Tuple, Optional

from ..geometry.geometry_utils import (
    copy_chain,
    angular_distance_between_chains,
    visualize_selected_ch_and_chains_over_image_,
    euclidean_distance_between_nodes,
    get_chain_from_list_by_id,
    minimum_euclidean_distance_between_chains_endpoints,
    get_chains_within_angle,
    get_closest_dots_to_angle_on_radial_direction_sorted_by_ascending_distance_to_center,
)
from ..geometry.node import Node
from ..geometry.angular_set import Set
from ..analysis.chain_system_manager import ChainSystemManager
from ..analysis.connect_parameters import ConnectParameters
from ..geometry.chain import Chain, TypeChains, EndPoints, ChainLocation
from ..geometry.node import Node
from ..analysis.interpolation_nodes import (
    compute_interpolation_domain,
    domain_interpolation,
)
from ..analysis.chain_analysis_tools import similarity_conditions
from ..config import config


def extract_border_chain_from_list(
    ch_s: List[Chain], nodes_s: List[Node]
) -> Tuple[Chain, List[Chain], List[Node]]:
    """
    Extract border chain from chain and nodes list.

    Args:
        ch_s (List[Chain]): Chain list.
        nodes_s (List[Node]): Node list.

    Returns:
        Tuple[Chain, List[Chain], List[Node]]: Border chain, chains without border, nodes without border.
    """
    ch_s_without_border = [chain for chain in ch_s if chain.type != TypeChains.border]
    border_chain = next(chain for chain in ch_s if (chain.type == TypeChains.border))
    nodes_s_without_border = [
        node for node in nodes_s if node.chain_id != border_chain.id
    ]

    return border_chain, ch_s_without_border, nodes_s_without_border


def copy_chains_and_nodes(ch_s: List[Chain]) -> Tuple[List[Chain], List[Node]]:
    """
    Copy chains and their nodes.

    Args:
        ch_s (List[Chain]): Chain list.

    Returns:
        Tuple[List[Chain], List[Node]]: Copied chains and their nodes.
    """
    nodes_s = []

    ch_s = [copy_chain(chain) for chain in ch_s]

    for chain in ch_s:
        nodes_s += chain.l_nodes

    return ch_s, nodes_s


def connect_chains(
    l_ch_s: List[Chain],
    img_pre: Optional[np.ndarray] = None,
) -> Tuple[List[Chain], List[Node]]:
    """
    Logic to connect chains. Same logic to connect chains is applied several times, smoothing restriction.
    Implements Algorithm 7 in the supplementary material.

    Args:
        l_ch_s (List[Chain]): Chain list.
        nr (int): Some integer parameter.
        debug (bool): Debug flag.
        img_pre (bool): Some boolean flag.
        output_dir (str): Output directory.

    Returns:
        Tuple[List[Chain], List[Node]]: Connected chains and their nodes.
    """
    # Copy ch_i and nodes
    l_ch_s, l_nodes_s = copy_chains_and_nodes(l_ch_s)
    # Paper Table 1 parameters initialization
    parameters = ConnectParameters(l_ch_s, l_nodes_s)

    m = compute_intersection_matrix(l_ch_s, l_nodes_s)

    # Iteration over the parameters, 9 iterations in total
    for i in range(parameters.iterations):
        # Get parameters for iteration i
        iteration_params = parameters.get_iteration_parameters(i)

        # debug_img_pre is a copy of the input image. It is used to visualize the results of the current iteration for debugging purposes.
        # Algorithm 2 in the paper
        l_ch_c, l_nodes_c, m = connect_chains_main_logic(
            m=m,
            nr=config.nr,
            debug_imgs=config.debug,
            img_pre=img_pre,
            save=f"{config.output_dir}/output_{i}_",
            **iteration_params,
        )

        # Update chain list and chain node list for next iteration
        parameters.update_list_for_next_iteration(l_ch_c, l_nodes_c)

    return l_ch_c, l_nodes_c


def update_pointer(
    ch_j: Chain, closest: Optional[Chain], l_candidates_chi: List[Chain]
) -> int:
    """
    Update the pointer for the chain.

    Args:
        ch_j (Chain): The current chain.
        closest (Optional[Chain]): The closest chain.
        l_candidates_chi (List[Chain]): List of candidate chains.

    Returns:
        int: The updated pointer.
    """
    ch_j_index = l_candidates_chi.index(ch_j)
    j_pointer = ch_j_index if closest is not None else ch_j_index + 1

    return j_pointer


def iterate_over_chains_list_and_complete_them_if_met_conditions(
    state: ChainSystemManager,
) -> Tuple[List[Chain], List[Node], np.ndarray]:
    """
    Iterate over the list of chains and complete them if conditions are met.

    Args:
        state (SystemStatus): The current system state.

    Returns:
        Tuple[List[Chain], List[Node], np.ndarray]: Updated chains, nodes, and intersection matrix.
    """
    for chain in state.l_ch_s:
        state.fill_chain_if_there_is_no_overlapping(chain)

    return state.l_ch_s, state.l_nodes_s, state.M


def debugging_chains(
    state: ChainSystemManager, chains_to_debug: List[Chain], filename: str
) -> None:
    """
    Debug the chains by visualizing them.

    Args:
        state (SystemStatus): The current system state.
        chains_to_debug (List[Chain]): List of chains to debug.
        filename (str): Filename to save the debug image.

    Returns:
        None
    """
    if state.debug:
        visualize_selected_ch_and_chains_over_image_(
            [ch for ch in chains_to_debug if ch is not None],
            state.l_ch_s,
            img=state.img,
            filename=filename,
        )
        state.counter += 1


def connect_chains_main_logic(
    m: np.ndarray,
    nr: int,
    l_ch_s: List[Chain],
    l_nodes_s: List[Node],
    th_radial_tolerance: float = 2,
    th_distribution_size: float = 2,
    th_regular_derivative: float = 1.5,
    neighbourhood_size: int = 22,
    derivative_from_center: bool = False,
    debug_imgs: bool = False,
    img_pre: Optional[np.ndarray] = None,
    save: Optional[str] = None,
) -> Tuple[List[Chain], List[Node], np.ndarray]:
    """
    Logic for connecting chains based on similarity conditions. Implements Algorithm 2 from the paper.

    Args:
        m (np.ndarray): Matrix of intersections between chains.
        nr (int): Number of rays.
        l_ch_s (List[Chain]): List of chains.
        l_nodes_s (List[Node]): List of nodes belonging to chains.
        th_radial_tolerance (float, optional): Threshold for radial tolerance. Defaults to 2.
        th_distribution_size (float, optional): Threshold for distribution size. Defaults to 2.
        th_regular_derivative (float, optional): Threshold for regular derivative. Defaults to 1.5.
        neighbourhood_size (int, optional): Size of neighbourhood in which we search for similar chains. Defaults to 22.
        derivative_from_center (bool, optional): If true, derivative is calculated from cy, otherwise from support chain. Defaults to False.
        debug_imgs (bool, optional): Debug parameter. Defaults to False.
        img_pre (Optional[np.ndarray], optional): Image for debug. Defaults to None.
        save (Optional[str], optional): Image save location. Debug only. Defaults to None.

    Returns:
        Tuple[List[Chain], List[Node], np.ndarray]: Nodes and chain list after connecting.
    """
    # Initialization of the state object. It contains all the information needed to connect chains.
    state = ChainSystemManager(
        l_ch_s,
        l_nodes_s,
        m,
        nr=nr,
        th_radial_tolerance=th_radial_tolerance,
        th_distribution_size=th_distribution_size,
        th_regular_derivative=th_regular_derivative,
        neighbourhood_size=neighbourhood_size,
        derivative_from_center=derivative_from_center,
        debug=debug_imgs,
        save=save,
        img=img_pre,
    )

    # State.continue_in_loop() check if current state is equal to the previous one. If it is, the algorithm stops.
    # If some chains have been connected in the current iteration, the algorithm continues one more iteration.
    # Additionaly, if nodes have been added to some chain, the algorithm continues one more iteration.
    while state.continue_in_loop():
        # Get next chain to be processed. Algorithm 11 in the paper.
        ch_i = state.get_next_chain()

        # Get chains in ch_i neighbourhood
        l_s_outward, l_s_inward = get_chains_in_and_out_wards(state.l_ch_s, ch_i)

        for location, l_candidates_chi in zip(
            [ChainLocation.inwards, ChainLocation.outwards],
            [l_s_inward, l_s_outward],
        ):
            j_pointer = 0
            while len(l_candidates_chi) > j_pointer:
                debugging_chains(
                    state,
                    [ch_i] + l_candidates_chi,
                    f"{state.path}/{state.counter}_0_{ch_i.label_id}_{location}.png",
                )
                ch_j = l_candidates_chi[j_pointer]

                debugging_chains(
                    state, [ch_i, ch_j], f"{state.path}/{state.counter}_1.png"
                )
                l_no_intersection_j = get_non_intersection_chains(
                    state.M, l_candidates_chi, ch_j
                )

                # Algorithm 13 in the supplementary material
                ch_k_b = get_closest_chain_logic(
                    state,
                    ch_j,
                    l_candidates_chi,
                    l_no_intersection_j,
                    ch_i,
                    location,
                    EndPoints.B,
                )
                debugging_chains(
                    state, [ch_i, ch_j, ch_k_b], f"{state.path}/{state.counter}_2.png"
                )

                # Algorithm 13 in the supplementary material
                ch_k_a = get_closest_chain_logic(
                    state,
                    ch_j,
                    l_candidates_chi,
                    l_no_intersection_j,
                    ch_i,
                    location,
                    EndPoints.A,
                )
                debugging_chains(
                    state, [ch_i, ch_j, ch_k_a], f"{state.path}/{state.counter}_3.png"
                )

                ch_k, endpoint = select_closest_chain(ch_j, ch_k_a, ch_k_b)
                debugging_chains(
                    state, [ch_i, ch_j, ch_k], f"{state.path}/{state.counter}_4.png"
                )

                # Algorithm 14 in the paper
                connect_two_chains(state, ch_j, ch_k, l_candidates_chi, endpoint, ch_i)
                debugging_chains(
                    state, [ch_i, ch_j], f"{state.path}/{state.counter}_5.png"
                )

                j_pointer = update_pointer(ch_j, ch_k, l_candidates_chi)

        # Implementing the logic of Algorithm 10
        state.update_system_status(ch_i, l_s_outward, l_s_inward)

    l_ch_c, l_nodes_c, intersection_matrix = (
        iterate_over_chains_list_and_complete_them_if_met_conditions(state)
    )
    debugging_chains(state, l_ch_c, f"{state.path}/{state.counter}.png")

    return l_ch_c, l_nodes_c, intersection_matrix


def intersection_chains(
    m: np.ndarray, candidate_chain: Chain, l_sorted_chains_in_neighbourhood: List[Chain]
) -> List[Chain]:
    """
    Find chains that intersect with the candidate chain.

    Args:
        m (np.ndarray): Intersection matrix.
        candidate_chain (Chain): The candidate chain.
        l_sorted_chains_in_neighbourhood (List[Chain]): Chains in the neighbourhood sorted by angular distance.

    Returns:
        List[Chain]: List of chains that intersect with the candidate chain.
    """
    inter_next_chain = np.where(m[candidate_chain.id] == 1)[0]
    l_intersections_candidate = [
        set.cad
        for set in l_sorted_chains_in_neighbourhood
        if set.cad.id in inter_next_chain and candidate_chain.id != set.cad.id
    ]

    return l_intersections_candidate


def get_all_chain_in_subset_that_satisfy_condition(
    state: ChainSystemManager,
    ch_j: Chain,
    ch_i: Chain,
    endpoint: int,
    radial_distance: float,
    candidate_chain: Chain,
    l_intersections_candidate: List[Chain],
) -> List[Set]:
    """
    Get all chains in the subset that satisfy the connectivity goodness condition.

    Args:
        state (SystemStatus): The current system state.
        ch_j (Chain): The current chain.
        ch_i (Chain): The support chain.
        endpoint (int): The endpoint of ch_j.
        radial_distance (float): Radial distance between ch_j and candidate chain.
        candidate_chain (Chain): The candidate chain.
        l_intersections_candidate (List[Chain]): List of chains that intersect with the candidate chain.

    Returns:
        List[Set]: List of sets that satisfy the connectivity goodness condition.
    """
    l_intersection_candidate_set = [Set(radial_distance, candidate_chain)]

    for chain_inter in l_intersections_candidate:
        pass_control, radial_distance = connectivity_goodness_condition(
            state, ch_j, chain_inter, ch_i, endpoint
        )
        if pass_control:
            l_intersection_candidate_set.append(Set(radial_distance, chain_inter))

    return l_intersection_candidate_set


def get_the_closest_chain_by_radial_distance_that_does_not_intersect(
    state: ChainSystemManager,
    ch_j: Chain,
    ch_i: Chain,
    endpoint: int,
    candidate_chain_radial_distance: float,
    candidate_chain: Chain,
    M: np.ndarray,
    l_sorted_chains_in_neighbourhood: List[Chain],
) -> Chain:
    """
    Implements Algorithm 14 in the supplementary material.

    Args:
        state (SystemStatus): Data structure with all the information of the system.
        ch_j (Chain): The current chain.
        ch_i (Chain): The support chain.
        endpoint (int): The endpoint of ch_j.
        candidate_chain_radial_distance (float): Radial distance between ch_j and candidate chain.
        candidate_chain (Chain): Angular closer chain to ch_j.
        M (np.ndarray): Intersection matrix.
        l_sorted_chains_in_neighbourhood (List[Chain]): Chains in ch_j endpoint neighbourhood sorted by angular distance.

    Returns:
        Chain: Closest chain to ch_j that satisfies connectivity goodness conditions.
    """
    # Get all the chains that intersect to candidate_chain
    l_intersections_candidate = intersection_chains(
        M, candidate_chain, l_sorted_chains_in_neighbourhood
    )

    # Get all the chains that intersect to candidate_chain and satisfy connectivity_goodness_condition with ch_j
    l_intersections_candidate_set = get_all_chain_in_subset_that_satisfy_condition(
        state,
        ch_j,
        ch_i,
        endpoint,
        candidate_chain_radial_distance,
        candidate_chain,
        l_intersections_candidate,
    )
    # Sort them by proximity to ch_j
    l_intersections_candidate_set.sort(key=lambda x: x.distance)

    # Return ch_k ch_i
    ch_k = l_intersections_candidate_set[0].cad

    return ch_k


def get_closest_chain(
    state: ChainSystemManager,
    ch_j: Chain,
    l_no_intersection_j: List[Chain],
    ch_i: Chain,
    location: int,
    endpoint: int,
    m: np.ndarray,
) -> Optional[Chain]:
    """
    Search for the closest chain to ch_j that does not intersect with ch_j and met conditions.
    Implements Algorithm 3 from the paper.

    Args:
        state (SystemStatus): System status instance.
        ch_j (Chain): Source chain.
        l_no_intersection_j (List[Chain]): List of chains that do not intersect with ch_j.
        ch_i (Chain): Support chain of ch_j.
        location (int): Inward or outward ch_j location regarding ch_i.
        endpoint (int): ch_j endpoint.
        m (np.ndarray): Intersection matrix.

    Returns:
        Optional[Chain]: The closest chain to ch_j.
    """
    # Sort chains by proximity
    neighbourhood_size = state.neighbourhood_size
    l_sorted_chains_in_neighbourhood = get_chains_in_neighbourhood(
        neighbourhood_size, l_no_intersection_j, ch_j, ch_i, endpoint, location
    )

    next_id = 0
    ch_k = None

    # Search for closest chain to ch_i
    lenght_chains = len(l_sorted_chains_in_neighbourhood)
    while next_id < lenght_chains:
        candidate_chain = l_sorted_chains_in_neighbourhood[next_id].cad

        # Algorithm 4 from paper.
        pass_control, radial_distance = connectivity_goodness_condition(
            state, ch_j, candidate_chain, ch_i, endpoint
        )

        if pass_control:
            # Check that do not exist other chains that intersect next ch_i that is radially ch_k to ch_j
            # Get chains that intersect next ch_i. Algorithm 14 in the supplementary material.
            ch_k = get_the_closest_chain_by_radial_distance_that_does_not_intersect(
                state,
                ch_j,
                ch_i,
                endpoint,
                radial_distance,
                candidate_chain,
                m,
                l_sorted_chains_in_neighbourhood,
            )

            break

        next_id += 1

    return ch_k


def get_closest_chain_logic(
    state: ChainSystemManager,
    ch_j: Chain,
    l_candidates_chi: List[Chain],
    l_no_intersection_j: List[Chain],
    ch_i: Chain,
    location: int,
    endpoint: int,
) -> Optional[Chain]:
    """
    Get the ch_k chain that met condition if it is symmetric. If it is not symmetric return None.
    Implements Algorithm 13 in the supplementary material.

    Args:
        state (SystemStatus): System status instance.
        ch_j (Chain): Chain that is going to be connected to another chain.
        l_candidates_chi (List[Chain]): List of chains that can be candidates to be connected to ch_j.
        l_no_intersection_j (List[Chain]): List of chains that do not intersect with ch_j.
        ch_i (Chain): Chain that supports ch_j.
        location (int): Location of ch_j regarding support chain (inward/outward).
        endpoint (int): Endpoint of ch_j that is going to be connected.

    Returns:
        Optional[Chain]: Closest chain, ch_k, to ch_j that met condition.
    """
    # Algorithm 3 in the paper
    ch_k = get_closest_chain(
        state, ch_j, l_no_intersection_j, ch_i, location, endpoint, state.M
    )

    if ch_k is None:
        return ch_k

    l_no_intersection_k = get_non_intersection_chains(state.M, l_candidates_chi, ch_k)

    endpoint_k = EndPoints.A if endpoint == EndPoints.B else EndPoints.B

    symmetric_chain = get_closest_chain(
        state, ch_k, l_no_intersection_k, ch_i, location, endpoint_k, state.M
    )

    ch_k = None if symmetric_chain != ch_j else ch_k
    if ch_k is not None and (ch_k.size + ch_j.size) > ch_k.nr:
        ch_k = None

    return ch_k


def move_nodes_from_one_chain_to_another(ch_j: Chain, ch_k: Chain) -> bool:
    """
    Move nodes from one chain to another.

    Args:
        ch_j (Chain): Destination chain.
        ch_k (Chain): Source chain.

    Returns:
        bool: Whether the border has changed.
    """
    for node in ch_k.l_nodes:
        node.chain_id = ch_j.id

    change_border = ch_j.add_nodes_list(ch_k.l_nodes)

    return change_border


def generate_new_nodes(
    state: ChainSystemManager, ch_j: Chain, ch_k: Chain, endpoint: int, ch_i: Chain
) -> None:
    """
    Generate new nodes between chains.

    Args:
        state (SystemStatus): System status instance.
        ch_j (Chain): Destination chain.
        ch_k (Chain): Source chain.
        endpoint (int): Endpoint of ch_j.
        ch_i (Chain): Support chain.
    """
    l_new_nodes = []

    ch_j_endpoint = ch_j.extA if endpoint == EndPoints.A else ch_j.extB
    ch_k_endpoint = ch_k.extB if endpoint == EndPoints.A else ch_k.extA

    domain_interpolation(
        ch_i, ch_j_endpoint, ch_k_endpoint, endpoint, ch_j, l_new_nodes
    )
    state.add_nodes_list_to_system(ch_j, l_new_nodes)

    return


def updating_chain_nodes(state: ChainSystemManager, ch_j: Chain, ch_k: Chain) -> None:
    """
    Update chain nodes after moving nodes from one chain to another.

    Args:
        state (SystemStatus): System status instance.
        ch_j (Chain): Destination chain.
        ch_k (Chain): Source chain.
    """
    change_border = move_nodes_from_one_chain_to_another(ch_j, ch_k)
    if change_border:
        state.update_chain_neighbourhood([ch_j])

    return


def delete_closest_chain(
    state: ChainSystemManager, ch_k: Chain, l_candidates_chi: List[Chain]
) -> None:
    """
    Delete the closest chain from the system.

    Args:
        state (SystemStatus): System status instance.
        ch_k (Chain): Chain to be deleted.
        l_candidates_chi (List[Chain]): List of candidate chains.
    """
    cad_2_index = state.l_ch_s.index(ch_k)
    del state.l_ch_s[cad_2_index]
    id_connected_chain = l_candidates_chi.index(ch_k)
    del l_candidates_chi[id_connected_chain]

    return


def update_intersection_matrix(
    state: ChainSystemManager, ch_j: Chain, ch_k: Chain
) -> None:
    """
    Update the intersection matrix after deleting a chain.

    Args:
        state (SystemStatus): System status instance.
        ch_j (Chain): Remaining chain.
        ch_k (Chain): Deleted chain.
    """
    inter_cad_1 = state.M[ch_j.id]
    inter_cad_2 = state.M[ch_k.id]
    or_inter_cad1_cad2 = np.logical_or(inter_cad_1, inter_cad_2)
    state.M[ch_j.id] = or_inter_cad1_cad2
    state.M[:, ch_j.id] = or_inter_cad1_cad2
    state.M = np.delete(state.M, ch_k.id, 1)
    state.M = np.delete(state.M, ch_k.id, 0)

    return


def update_chains_ids(state: ChainSystemManager, ch_k: Chain) -> None:
    """
    Update chain IDs after deleting a chain.

    Args:
        state (SystemStatus): System status instance.
        ch_k (Chain): Deleted chain.
    """
    for ch_old in state.l_ch_s:
        if ch_old.id > ch_k.id:
            new_id = ch_old.id - 1
            ch_old.change_id(new_id)

    return


def connect_two_chains(
    state: ChainSystemManager,
    ch_j: Chain,
    ch_k: Chain,
    l_candidates_chi: List[Chain],
    endpoint: int,
    ch_i: Chain,
) -> None:
    """
    Algorithm 12 in the supplementary material. Connect chains ch_j and ch_k updating all the information about the system.

    Args:
        state (SystemStatus): Class object that contains all the information about the system.
        ch_j (Chain): Chain j to connect.
        ch_k (Chain): Chain k to connect.
        l_candidates_chi (List[Chain]): List of chains that have support chain ch_i.
        endpoint (int): Endpoint of ch_j that is going to be connected.
        ch_i (Chain): Support chain.

    Returns:
        None
    """
    if endpoint is None:
        return

    if ch_j == ch_k:
        return

    # Generate new dots
    generate_new_nodes(state, ch_j, ch_k, endpoint, ch_i)

    # move node from one ch_i to another
    updating_chain_nodes(state, ch_j, ch_k)

    # update chains
    update_chain_after_connect(state, ch_j, ch_k)

    # delete ch_k from  list l_candidate_chi  and state.l_ch_s
    delete_closest_chain(state, ch_k, l_candidates_chi)

    # update intersection matrix
    update_intersection_matrix(state, ch_j, ch_k)

    # update ch_i ids
    update_chains_ids(state, ch_k)

    return


def get_inward_and_outward_list_chains_via_pointers(
    l_ch_s: List[Chain], support_chain: Chain
) -> Tuple[List[Chain], List[Chain]]:
    """
    Get the inward and outward chains of ch_i.

    Args:
        l_ch_s (List[Chain]): List of chains.
        support_chain (Chain): Support chain, ch_i, to get the inward and outward chains.

    Returns:
        Tuple[List[Chain], List[Chain]]: Inward and outward list chains.
    """
    l_s_outward = []
    l_s_inward = []

    for ch_cand in l_ch_s:
        if ch_cand == support_chain:
            continue
        a_outward, b_outward, a_inward, b_inward = (
            ch_cand.A_outward,
            ch_cand.B_outward,
            ch_cand.A_inward,
            ch_cand.B_inward,
        )

        if (ch_cand not in l_s_outward) and (
            (a_inward is not None and support_chain is a_inward)
            or (b_inward is not None and support_chain is b_inward)
        ):
            l_s_outward.append(ch_cand)

        if (ch_cand not in l_s_inward) and (
            (a_outward is not None and support_chain is a_outward)
            or (b_outward is not None and support_chain is b_outward)
        ):
            l_s_inward.append(ch_cand)

    return l_s_outward, l_s_inward


def get_non_intersection_chains(
    M: np.ndarray, l_candidates_chi: List[Chain], ch_j: Chain
) -> List[Chain]:
    """
    Get the list of chains that do not intersect with ch_j.

    Args:
        M (np.ndarray): Intersection matrix.
        l_candidates_chi (List[Chain]): List of chains.
        ch_j (Chain): Chain j.

    Returns:
        List[Chain]: List of chains that do not intersect with ch_j.
    """
    id_inter = np.where(M[ch_j.id] == 1)[0]
    candidates_chi_non_chj_intersection = [
        cad for cad in l_candidates_chi if cad.id not in id_inter
    ]

    return candidates_chi_non_chj_intersection


def get_intersection_chains(
    M: np.ndarray, l_candidates_chi: List[Chain], ch_j: Chain
) -> List[Chain]:
    """
    Get the list of chains that intersect with ch_j.

    Args:
        M (np.ndarray): Intersection matrix.
        l_candidates_chi (List[Chain]): List of chains.
        ch_j (Chain): Chain j.

    Returns:
        List[Chain]: List of chains that intersect with ch_j.
    """
    id_inter = np.where(M[ch_j.id] == 1)[0]
    candidates_chi_non_chj_intersection = [
        cad for cad in l_candidates_chi if cad.id in id_inter
    ]

    return candidates_chi_non_chj_intersection


def remove_chains_if_present_at_both_groups(
    S_up: List[Chain], S_down: List[Chain]
) -> List[Chain]:
    """
    Remove chains if present in both groups.

    Args:
        S_up (List[Chain]): List of chains in the upward group.
        S_down (List[Chain]): List of chains in the downward group.

    Returns:
        List[Chain]: List of chains present in both groups.
    """
    up_down = [cad for cad in S_up if cad in S_down]
    for cad in up_down:
        S_up.remove(cad)

    return up_down


def get_chains_in_and_out_wards(
    l_ch_s: List[Chain], support_chain: Chain
) -> Tuple[List[Chain], List[Chain]]:
    """
    Get chains inwards and outwards from l_ch_s given support chain, ch_i.

    Args:
        l_ch_s (List[Chain]): List of chains.
        support_chain (Chain): Support chain, ch_i.

    Returns:
        Tuple[List[Chain], List[Chain]]: List of chains inwards and list of chains outwards.
    """
    l_s_outward, l_s_inward = get_inward_and_outward_list_chains_via_pointers(
        l_ch_s, support_chain
    )
    remove_chains_if_present_at_both_groups(l_s_outward, l_s_inward)

    return l_s_outward, l_s_inward


def select_closest_chain(
    chain: Chain, a_neighbour_chain: Optional[Chain], b_neighbour_chain: Optional[Chain]
) -> Tuple[Optional[Chain], Optional[int]]:
    """
    Select the closest chain to the given chain.

    Args:
        chain (Chain): The reference chain.
        a_neighbour_chain (Optional[Chain]): Neighbour chain at endpoint A.
        b_neighbour_chain (Optional[Chain]): Neighbour chain at endpoint B.

    Returns:
        Tuple[Optional[Chain], Optional[int]]: Closest chain and its endpoint.
    """
    if a_neighbour_chain is not None:
        d_a = distance_between_border(chain, a_neighbour_chain, EndPoints.A)
    else:
        d_a = -1

    if b_neighbour_chain is not None:
        d_b = distance_between_border(chain, b_neighbour_chain, EndPoints.B)
    else:
        d_b = -1

    if d_a == d_b == -1:
        closest_chain = None
        endpoint = None

    elif d_a >= d_b:
        closest_chain = a_neighbour_chain
        endpoint = EndPoints.A

    elif d_b > d_a:
        closest_chain = b_neighbour_chain
        endpoint = EndPoints.B

    else:
        raise

    return closest_chain, endpoint


def get_chains_in_neighbourhood(
    neighbourhood_size: float,
    l_no_intersection_j: List[Chain],
    ch_j: Chain,
    ch_i: Chain,
    endpoint: int,
    location: int,
) -> List[Set]:
    """
    Get all the chains in the neighbourhood of the chain ch_j included in the list no_intersection_j.

    Args:
        neighbourhood_size (float): Angular neighbourhood size.
        l_no_intersection_j (List[Chain]): List of chains that do not intersect with ch_j.
        ch_j (Chain): Chain j.
        ch_i (Chain): Support chain, ch_i.
        endpoint (int): ch_j endpoint.
        location (int): Inward or outward location.

    Returns:
        List[Set]: List of chains in the neighbourhood of ch_j.
    """
    l_chains_in_neighbourhood = []

    for cand_chain in l_no_intersection_j:
        angular_distance = angular_distance_between_chains(ch_j, cand_chain, endpoint)
        if angular_distance < neighbourhood_size and cand_chain.id != ch_j.id:
            l_chains_in_neighbourhood.append(Set(angular_distance, cand_chain))

    if endpoint == EndPoints.A and location == ChainLocation.inwards:
        l_chains_in_neighbourhood = [
            element
            for element in l_chains_in_neighbourhood
            if element.cad.B_outward == ch_i
        ]

    elif endpoint == EndPoints.A and location == ChainLocation.outwards:
        l_chains_in_neighbourhood = [
            element
            for element in l_chains_in_neighbourhood
            if element.cad.B_inward == ch_i
        ]
    elif endpoint == EndPoints.B and location == ChainLocation.inwards:
        l_chains_in_neighbourhood = [
            element
            for element in l_chains_in_neighbourhood
            if element.cad.A_outward == ch_i
        ]

    elif endpoint == EndPoints.B and location == ChainLocation.outwards:
        l_chains_in_neighbourhood = [
            element
            for element in l_chains_in_neighbourhood
            if element.cad.A_inward == ch_i
        ]

    l_sorted_chains_in_neighbourhood = sort_chains_in_neighbourhood(
        l_chains_in_neighbourhood, ch_j
    )

    return l_sorted_chains_in_neighbourhood


def sort_chains_in_neighbourhood(
    chains_in_neighbourhood: List[Set], ch_j: Chain
) -> List[Set]:
    """
    Sort chains by angular distance. Set of chains with same angular distance, are sorted by euclidean distance to ch_j.

    Args:
        chains_in_neighbourhood (List[Set]): List of Sets. A set elements is composed by a chain and a distance between support chain and ch_j.
        ch_j (Chain): Chain j.

    Returns:
        List[Set]: Sorted list of chains in the neighbourhood.
    """
    sorted_chains_in_neighbourhood = []

    unique_angular_distances = np.unique(
        [conj.distance for conj in chains_in_neighbourhood]
    )

    for d in unique_angular_distances:
        chains_same_angular_distance = [
            conj.cad for conj in chains_in_neighbourhood if conj.distance == d
        ]
        euclidean_distance_set = [
            Set(minimum_euclidean_distance_between_chains_endpoints(ch_d, ch_j), ch_d)
            for ch_d in chains_same_angular_distance
        ]
        euclidean_distance_set.sort(key=lambda x: x.distance)
        sorted_chains_in_neighbourhood += [
            Set(d, set.cad) for set in euclidean_distance_set
        ]

    return sorted_chains_in_neighbourhood


def check_endpoints(
    support_chain: Chain, ch_j: Chain, candidate_chain: Chain, endpoint: int
) -> bool:
    """
    Check if the endpoints of the chain ch_j are in the interpolation domain of the support chain, ch_i.

    Args:
        support_chain (Chain): Support chain of ch_j and candidate_chain.
        ch_j (Chain): Chain j.
        candidate_chain (Chain): Candidate chain.
        endpoint (int): ch_j endpoint.

    Returns:
        bool: True if the endpoints are in the interpolation domain, False otherwise.
    """
    support_chain_angular_domain = support_chain.get_dot_angle_values()
    ext_cad_1 = ch_j.extA if endpoint == EndPoints.A else ch_j.extB
    ext_cad_2 = (
        candidate_chain.extB if endpoint == EndPoints.A else candidate_chain.extA
    )
    interpolation_domain = compute_interpolation_domain(
        endpoint, ext_cad_1, ext_cad_2, support_chain.nr
    )
    intersection = np.intersect1d(interpolation_domain, support_chain_angular_domain)

    return True if len(intersection) == len(interpolation_domain) else False


def connectivity_goodness_condition(
    state: ChainSystemManager,
    ch_j: Chain,
    candidate_chain: Chain,
    ch_i: Chain,
    endpoint: int,
) -> Tuple[bool, float]:
    """
    Check if the chain candidate_chain can be connected to the chain ch_j.
    Implements Algorithm 4 of the paper.

    Args:
        state (SystemStatus): System status.
        ch_j (Chain): Chain j.
        candidate_chain (Chain): Candidate chain.
        ch_i (Chain): Support chain.
        endpoint (int): ch_j endpoint.

    Returns:
        Tuple[bool, float]: True if the chain candidate_chain can be connected to the chain ch_j, and the radial distance.
    """
    # Size criterion
    if ch_j.size + candidate_chain.size > ch_j.nr:
        return (False, -1)

    # Connect chains by correct endpoint
    check_pass = check_endpoints(ch_i, ch_j, candidate_chain, endpoint)
    if not check_pass:
        return (False, -1)

    # Radial check
    check_pass, distribution_distance = similarity_conditions(
        state,
        state.th_radial_tolerance,
        state.th_distribution_size,
        state.th_regular_derivative,
        state.derivative_from_center,
        ch_i,
        ch_j,
        candidate_chain,
        endpoint,
    )

    return (check_pass, distribution_distance)


def get_ids_chain_intersection(state: ChainSystemManager, chain_id: int) -> List[int]:
    """
    Get the IDs of chains that intersect with the given chain.

    Args:
        state (SystemStatus): System status.
        chain_id (int): ID of the chain.

    Returns:
        List[int]: List of IDs of intersecting chains.
    """
    ids_interseccion = list(np.where(state.M[chain_id] == 1)[0])
    ids_interseccion.remove(chain_id)

    return ids_interseccion


def distance_between_border(chain_1: Chain, chain_2: Chain, border_1: int) -> float:
    """
    Calculate the distance between the borders of two chains.

    Args:
        chain_1 (Chain): First chain.
        chain_2 (Chain): Second chain.
        border_1 (int): Border of the first chain.

    Returns:
        float: Distance between the borders.
    """
    node1 = chain_1.extA if border_1 == EndPoints.A else chain_2.extB
    node2 = chain_2.extB if border_1 == EndPoints.A else chain_2.extA

    d = euclidean_distance_between_nodes(node1, node2)

    return d


def get_inward_and_outward_visible_chains(
    chain_list: List[Chain], chain: Chain, endpoint: int
) -> Tuple[Optional[Chain], Optional[Chain], Node]:
    """
    Get the inward and outward visible chains from the given chain and endpoint.

    Args:
        chain_list (List[Chain]): List of chains.
        chain (Chain): Reference chain.
        endpoint (int): Endpoint of the reference chain.

    Returns:
        Tuple[Optional[Chain], Optional[Chain], Node]: Inward chain, outward chain, and node direction.
    """
    node_direction = chain.extA if endpoint == EndPoints.A else chain.extB
    inward_chain = None
    outward_chain = None

    dot_chain_index, dots_over_ray_direction = get_dots_in_radial_direction(
        node_direction, chain_list
    )
    if dot_chain_index < 0:
        return None, None, node_direction

    if dot_chain_index > 0:
        down_dot = dots_over_ray_direction[dot_chain_index - 1]
        inward_chain = get_chain_from_list_by_id(chain_list, down_dot.chain_id)

    if len(dots_over_ray_direction) - 1 > dot_chain_index:
        up_dot = dots_over_ray_direction[dot_chain_index + 1]
        outward_chain = get_chain_from_list_by_id(chain_list, up_dot.chain_id)

    return inward_chain, outward_chain, node_direction


def get_dots_in_radial_direction(
    node_direction: Node, chain_list: List[Chain]
) -> Tuple[int, List[Node]]:
    """
    Get the dots in the radial direction from the given node direction.

    Args:
        node_direction (Node): Node direction.
        chain_list (List[Chain]): List of chains.

    Returns:
        Tuple[int, List[Node]]: Index of the dot chain and list of nodes over the ray direction.
    """
    chains_in_radial_direction = get_chains_within_angle(
        node_direction.angle, chain_list
    )
    nodes_over_ray = get_closest_dots_to_angle_on_radial_direction_sorted_by_ascending_distance_to_center(
        chains_in_radial_direction, node_direction.angle
    )

    list_dot_chain_index = [
        idx
        for idx, node in enumerate(nodes_over_ray)
        if node.chain_id == node_direction.chain_id
    ]
    if len(list_dot_chain_index) > 0:
        dot_chain_index = list_dot_chain_index[0]
    else:
        nodes_over_ray = []
        dot_chain_index = -1

    return dot_chain_index, nodes_over_ray


def update_chain_after_connect(
    state: ChainSystemManager, ch_j: Chain, ch_k: Chain
) -> int:
    """
    Update the chain information after connecting two chains.

    Args:
        state (SystemStatus): System status.
        ch_j (Chain): Chain j.
        ch_k (Chain): Chain k.

    Returns:
        int: Status code (0 for success).
    """
    for chain in state.l_ch_s:
        if chain.A_outward is not None:
            if chain.A_outward.id == ch_k.id:
                chain.A_outward = ch_j
        if chain.A_inward is not None:
            if chain.A_inward.id == ch_k.id:
                chain.A_inward = ch_j

        if chain.B_outward is not None:
            if chain.B_outward.id == ch_k.id:
                chain.B_outward = ch_j

        if chain.B_inward is not None:
            if chain.B_inward.id == ch_k.id:
                chain.B_inward = ch_j

    return 0


def intersection_between_chains(chain1: Chain, chain2: Chain) -> bool:
    """
    Check if there is an intersection between two chains.

    Args:
        chain1 (Chain): First chain.
        chain2 (Chain): Second chain.

    Returns:
        bool: True if there is an intersection, False otherwise.
    """
    angle_intersection = [
        node.angle for node in chain1.l_nodes if chain2.get_node_by_angle(node.angle)
    ]

    return True if len(angle_intersection) > 0 else False


def compute_intersection_matrix(
    chains_list: List[Chain], nodes_list: List[Node]
) -> np.ndarray:
    """
    Compute intersection matrix. If chain_i intersection chain_j then img_height[i,j] == img_height[j,i] == 1 else 0

    Args:
        chains_list: chains list
        nodes_list: nodes list
        nr: total rays in disk

    Returns:
        img_height: Square matrix of lenght len(l_ch_s).
    """
    m = np.eye(len(chains_list))

    for angle in np.arange(0, 360, 360 / config.nr):
        chains_id_over_direction = np.unique(
            [node.chain_id for node in nodes_list if node.angle == angle]
        )
        x, y = np.meshgrid(chains_id_over_direction, chains_id_over_direction)
        m[x, y] = 1

    return m
