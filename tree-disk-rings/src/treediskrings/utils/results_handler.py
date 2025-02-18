from typing import Optional, Tuple, List, Dict, Any
import numpy as np
import logging
import matplotlib.pyplot as plt

from ..geometry.curve import Curve
from ..geometry.chain import Chain, TypeChains
from ..processing.preprocessing import resize_image_using_pil_lib
from ..utils.file_utils import write_json
from ..geometry.geometry_utils import generate_visualization
from ..config import config

logger = logging.getLogger(__name__)


def get_completed_chains(chains: List[Chain]) -> List[Chain]:
    """Get filtered chains for output visualization."""
    return [
        chain
        for chain in chains
        if chain.is_closed()
        and chain.type not in [TypeChains.center, TypeChains.border]
    ]


def save_results(
    img_in: np.ndarray,
    img_pre: np.ndarray,
    devernay_edges: np.ndarray,
    devernay_curves_f: List[Curve],
    devernay_curves_s: List[Chain],
    devernay_curves_c: Optional[List[Chain]] = None,
    devernay_curves_p: Optional[List[Chain]] = None,
    save_to_disk: bool = True,
) -> Dict[str, np.ndarray]:
    """Save detection results to disk and return rendered visualizations."""

    # Save labelme JSON
    if save_to_disk and devernay_curves_p:
        labelme_data = chain_to_labelme(img_in, chain_list=devernay_curves_p)
        json_path = config.output_dir / "labelme.json"
        write_json(labelme_data, json_path)
        logger.info(f"Saved labelme JSON to {json_path}")

    # Resize if necessary
    m, n, _ = img_in.shape
    m_n, n_n = img_pre.shape
    if m != m_n:
        img_in = resize_image_using_pil_lib(img_in, m_n, n_n)

    # Generate all visualizations
    visualizations = {
        "input": img_in,
        "preprocessing": img_pre,
        "edges": generate_visualization(img=img_pre, devernay=devernay_edges),
        "filter": generate_visualization(img=img_pre, filter=devernay_curves_f),
        "chains": generate_visualization(img=img_in, chain_list=devernay_curves_s),
    }

    # Add optional visualizations
    if devernay_curves_c is not None:
        visualizations["connect"] = generate_visualization(
            img=img_in, chain_list=devernay_curves_c
        )

    if devernay_curves_p is not None:
        visualizations["postprocessing"] = generate_visualization(
            img=img_in, chain_list=devernay_curves_p
        )
        visualizations["output"] = generate_visualization(
            img=img_in, chain_list=get_completed_chains(devernay_curves_p)
        )

    # Save visualizations to disk
    if save_to_disk:
        for name, img in visualizations.items():
            output_path = config.output_dir / f"{name}.png"
            plt.imsave(str(output_path), img)
            logger.debug(f"Saved visualization to {output_path}")

    return visualizations


def chain_to_labelme(img_in: np.ndarray, chain_list: List[Chain]) -> Dict[str, Any]:
    """
    Convert chains to labelme format.
    The JSON is formatted to use the input image as the background and the chains as polygons.
    """
    init_height, init_width, _ = img_in.shape

    completed_chains = get_completed_chains(chain_list)

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
        "center": [
            (config.cy * height_cte) if config.cy is not None else None,
            (config.cx * width_cte) if config.cx is not None else None,
        ],
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
