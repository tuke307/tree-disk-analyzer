from typing import Any, List, Tuple

import cv2
import numpy as np
from shapely.geometry import Point

from ..geometry.chain import (
    Chain,
    Node,
    TypeChains,
)
from ..visualization.drawing import Drawing
from ..geometry.ray import Ray
from ..geometry.curve import Curve
from ..geometry.geometry_utils import euclidean_distance, get_node_from_list_by_angle
from ..config import config


def build_rays(m: int, n: int, center: Tuple[float, float]) -> List[Ray]:
    """
    Builds a list of rays emanating from the center at evenly spaced angles.

    Args:
        m (int): Height of the image.
        n (int): Width of the image.
        center (Tuple[float, float]): Center coordinates (y, x).

    Returns:
        List[Ray]: List of Ray objects.
    """
    angles_range = np.arange(0, 360, 360 / config.nr)
    radii_list = [Ray(direction, center, m, n) for direction in angles_range]
    return radii_list


def get_coordinates_from_intersection(inter: Any) -> Tuple[float, float]:
    """
    Formats the coordinates from a Shapely intersection object.

    Args:
        inter (Any): Intersection object.

    Returns:
        Tuple[float, float]: Coordinates (y, x) of the intersection point.
    """
    if "MULTI" in inter.wkt:
        inter = inter.geoms[0]

    if isinstance(inter, Point):
        y, x = inter.xy
        y, x = y[0], x[0]
    elif "LINESTRING" in inter.wkt:
        y, x = inter.xy
        y, x = y[1], x[1]
    elif "STRING" in inter.wkt:
        y, x = inter.coords.xy
        y, x = y[0], x[0]
    else:
        raise ValueError("Unsupported intersection type")

    return y, x


def compute_intersection(
    l_rays: List[Ray], curve: Curve, chain_id: int, center: Tuple[float, float]
) -> List[Node]:
    """
    Computes the intersection between rays and a Devernay curve.

    Args:
        l_rays (List[Ray]): List of rays.
        curve (Curve): Devernay curve with a 'geometry' attribute.
        chain_id (int): Chain identifier.
        center (Tuple[float, float]): Center coordinates (y, x).

    Returns:
        List[Node]: List of nodes resulting from the intersections.
    """
    l_curve_nodes = []
    for radii in l_rays:
        inter = radii.geometry.intersection(curve.geometry)
        if not inter.is_empty:
            try:
                y, x = get_coordinates_from_intersection(inter)
            except NotImplementedError:
                continue
            i, j = np.array(y), np.array(x)
            params = {
                "y": i,
                "x": j,
                "angle": int(radii.direction),
                "radial_distance": euclidean_distance([i, j], center),
                "chain_id": chain_id,
            }

            dot = Node(**params)
            if (
                dot not in l_curve_nodes
                and get_node_from_list_by_angle(l_curve_nodes, radii.direction) is None
            ):
                l_curve_nodes.append(dot)

    return l_curve_nodes


def intersections_between_rays_and_devernay_curves(
    l_rays: List[Ray],
    l_curves: List[Curve],
    center: Tuple[float, float],
    height: int,
    width: int,
) -> Tuple[List[Node], List[Chain]]:
    """
    Computes chains by sampling Devernay curves. Sampling is performed by finding the intersection
    between rays and Devernay curves.

    Args:
        center (Tuple[float, float]): Center coordinates (y, x).
        l_rays (List[Ray]): List of rays.
        l_curves (List[Curve]): List of Devernay curves.
        height (int): Height of the image.
        width (int): Width of the image.

    Returns:
        Tuple[List[Node], List[Chain]]: List of nodes and list of chains.
    """
    l_chain, l_nodes = [], []

    for idx, curve in enumerate(l_curves):
        chain_id = len(l_chain)
        l_curve_nodes = compute_intersection(l_rays, curve, chain_id, center)

        if len(l_curve_nodes) < config.min_chain_length:
            continue

        l_nodes += l_curve_nodes
        chain = Chain(
            chain_id, config.nr, center=center, img_height=height, img_width=width
        )
        chain.add_nodes_list(l_curve_nodes)
        l_chain.append(chain)

    # Devernay border curve is the last element of the list l_curves.
    if l_chain:
        l_chain[-1].type = TypeChains.border

    return l_nodes, l_chain


def generate_virtual_center_chain(
    chains_list: List[Chain],
    nodes_list: List[Node],
    height: int,
    width: int,
) -> None:
    """
    Generates a virtual center chain. This chain is used to connect the other chains.

    Args:
        chains_list (List[Chain]): List of chains.
        nodes_list (List[Node]): List of nodes.
        height (int): Height of the image.
        width (int): Width of the image.

    Returns:
        None
    """
    chain_id = len(chains_list)
    center_list = [
        Node(
            x=config.cx,
            y=config.cy,
            angle=angle,
            radial_distance=0,
            chain_id=chain_id,
        )
        for angle in np.arange(0, 360, 360 / config.nr)
    ]
    nodes_list += center_list

    chain = Chain(
        chain_id,
        config.nr,
        center=chains_list[0].center if chains_list else (config.cy, config.cx),
        img_height=height,
        img_width=width,
        type=TypeChains.center,
    )
    chain.add_nodes_list(center_list)

    chains_list.append(chain)

    # Set border chain as the last element of the list
    if len(chains_list) >= 2:
        chains_list[-2].change_id(len(chains_list) - 1)


def draw_ray_curve_and_intersections(
    dots_lists: List[Node],
    rays_list: List[Ray],
    curves_list: List[Curve],
    img_draw: np.ndarray,
    filename: str,
) -> None:
    """
    Draws rays, curves, and intersections on an image and saves it.

    Args:
        dots_lists (List[Node]): List of nodes representing intersections.
        rays_list (List[Ray]): List of rays.
        curves_list (List[Curve]): List of curves.
        img_draw (np.ndarray): Image array to draw on.
        filename (str): Filename to save the image.

    Returns:
        None
    """
    for ray in rays_list:
        img_draw = Drawing.radii(ray, img_draw)

    for curve in curves_list:
        img_draw = Drawing.curve(curve, img_draw)

    for dot in dots_lists:
        img_draw = Drawing.intersection(dot, img_draw)

    cv2.imwrite(filename, img_draw)


def sampling_edges(
    l_ch_f: List[Curve],
    img_pre: np.ndarray,
) -> Tuple[List[Chain], List[Node]]:
    """
    Samples Devernay curves using ray directions. Implements Algorithm 6 in the supplementary material.

    Args:
        l_ch_f (List[Curve]): Devernay curves.
        img_pre (np.ndarray): Input image.

    Returns:
        Tuple[List[Chain], List[Node]]:
            - l_ch_s: Sampled edges curves (list of Chain objects).
            - l_nodes_s: List of nodes.
    """
    height, width = img_pre.shape[:2]
    center = (config.cy, config.cx)

    l_rays = build_rays(height, width, center)
    l_nodes_s, l_ch_s = intersections_between_rays_and_devernay_curves(
        l_rays, l_ch_f, center, height, width
    )
    generate_virtual_center_chain(l_ch_s, l_nodes_s, height, width)

    # Debug purposes, not illustrated in the paper
    if config.debug:
        img_draw = np.zeros((img_pre.shape[0], img_pre.shape[1], 3), dtype=np.uint8)
        draw_ray_curve_and_intersections(
            l_nodes_s,
            l_rays,
            l_ch_f,
            img_draw,
            f"{config.output_dir}/dots_curve_and_rays.png",
        )

    return l_ch_s, l_nodes_s
