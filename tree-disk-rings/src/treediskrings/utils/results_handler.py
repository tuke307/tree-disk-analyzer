from typing import Tuple, List, Dict, Any
import numpy as np
import logging

from ..geometry.curve import Curve
from ..geometry.chain import Chain, TypeChains
from ..processing.preprocessing import resize_image_using_pil_lib
from ..utils.file_utils import write_json
from ..geometry.geometry_utils import visualize_chains_over_image
from ..config import config

logger = logging.getLogger(__name__)


def save_results(
    img_in: np.ndarray,
    img_pre: np.ndarray,
    devernay_edges: np.ndarray,
    devernay_curves_f: List[Curve],
    devernay_curves_s: List[Chain],
    devernay_curves_c: List[Chain],
    devernay_curves_p: List[Chain],
) -> None:
    """Save detection results to disk."""
    # Convert chains to labelme format
    labelme_data = chain_to_labelme(img_in, chain_list=devernay_curves_p)
    json_path = config.output_dir / "labelme.json"
    write_json(labelme_data, json_path)
    logger.info(f"Saved labelme JSON to {json_path}")

    # Resize if necessary
    m, n, _ = img_in.shape
    m_n, n_n = img_pre.shape
    if m != m_n:
        img_in = resize_image_using_pil_lib(img_in, m_n, n_n)

    # Save visualization images
    visualizations = {
        "input.png": (img_in, {}),
        "preprocessing.png": (img_pre, {}),
        "edges.png": (img_pre, {"devernay": devernay_edges}),
        "filter.png": (img_pre, {"filter": devernay_curves_f}),
        "chains.png": (img_in, {"chain_list": devernay_curves_s}),
        "connect.png": (img_in, {"chain_list": devernay_curves_c}),
        "postprocessing.png": (img_in, {"chain_list": devernay_curves_p}),
        "output.png": (
            img_in,
            {
                "chain_list": [
                    chain
                    for chain in devernay_curves_p
                    if chain.is_closed()
                    and chain.type not in [TypeChains.center, TypeChains.border]
                ]
            },
        ),
    }

    for filename, (img, kwargs) in visualizations.items():
        output_path = config.output_dir / filename
        visualize_chains_over_image(img=img, filename=str(output_path), **kwargs)
        logger.debug(f"Saved visualization to {output_path}")


def chain_to_labelme(img_in: np.ndarray, chain_list: List[Chain]) -> Dict[str, Any]:
    """
    Convert chains to labelme format.
    The JSON is formatted to use the input image as the background and the chains as polygons.
    """
    init_height, init_width, _ = img_in.shape

    completed_chains = [
        chain
        for chain in chain_list
        if chain.is_closed()
        and chain.type not in [TypeChains.center, TypeChains.border]
    ]

    width_cte = init_width / config.output_width if config.output_width != None else 1
    height_cte = (
        init_height / config.output_height if config.output_height != None else 1
    )

    labelme_json = {
        "imagePath": str(config.input_image),
        "imageHeight": init_height,
        "imageWidth": init_width,
        "version": "5.5.0",
        "flags": {},
        "shapes": [],
        "imageData": None,
        "center": [config.cy * height_cte, config.cx * width_cte],
    }

    for idx, chain in enumerate(completed_chains):
        ring = {
            "label": str(idx + 1),
            "points": [
                [node.x * width_cte, node.y * height_cte] for node in chain.l_nodes
            ],
            "shape_type": "polygon",
            "flags": {},
        }
        labelme_json["shapes"].append(ring)

    return labelme_json
