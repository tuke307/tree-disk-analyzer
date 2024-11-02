from typing import Tuple, List, Dict, Any
import numpy as np
import logging

from ..geometry.curve import Curve
from ..geometry.chain import Chain, TypeChains
from ..processing.preprocessing import resize
from ..utils.file_utils import write_json
from ..geometry.geometry_utils import visualize_chains_over_image
from ..config import Config

logger = logging.getLogger(__name__)


def save_results(
    res: Tuple[
        np.ndarray,
        np.ndarray,
        np.ndarray,
        List[Curve],
        List[Chain],
        List[Chain],
        List[Chain],
    ],
    config: Config,
) -> None:
    """Save detection results to disk."""
    im_seg, im_pre, ch_e, ch_f, ch_s, ch_c, ch_p = res

    # Convert chains to labelme format
    labelme_data = chain_to_labelme(
        chain_list=ch_p,
        image_height=config.height,
        image_width=config.width,
        cy=config.cy,
        cx=config.cx,
        img_orig=im_seg,
        image_path=str(config.input_image_path),
    )
    json_path = config.output_dir / "labelme.json"
    write_json(labelme_data, json_path)
    logger.info(f"Saved labelme JSON to {json_path}")

    if not config.save_imgs:
        return

    # Resize if necessary
    m, n, _ = im_seg.shape
    m_n, n_n = im_pre.shape
    if m != m_n:
        im_seg, _, _ = resize(im_seg, m_n, n_n)

    # Save visualization images
    visualizations = {
        "segmentation.png": (im_seg, {}),
        "preprocessing.png": (im_pre, {}),
        "edges.png": (im_pre, {"devernay": ch_e}),
        "filter.png": (im_pre, {"filter": ch_f}),
        "chains.png": (im_seg, {"chain_list": ch_s}),
        "connect.png": (im_seg, {"chain_list": ch_c}),
        "postprocessing.png": (im_seg, {"chain_list": ch_p}),
        "output.png": (
            im_seg,
            {
                "chain_list": [
                    chain
                    for chain in ch_p
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


def chain_to_labelme(
    chain_list: List[Chain],
    image_height: int,
    image_width: int,
    cy: int,
    cx: int,
    img_orig: np.ndarray,
    image_path: str,
) -> Dict[str, Any]:
    """Convert chains to labelme format."""
    init_height, init_width, _ = img_orig.shape

    completed_chains = [
        chain
        for chain in chain_list
        if chain.is_closed()
        and chain.type not in [TypeChains.center, TypeChains.border]
    ]

    width_cte = init_width / image_width if image_width != 0 else 1
    height_cte = init_height / image_height if image_height != 0 else 1

    labelme_json = {
        "imagePath": image_path,
        "imageHeight": init_height,
        "imageWidth": init_width,
        "version": "5.5.0",
        "flags": {},
        "shapes": [],
        "imageData": None,
        "center": [cy * height_cte, cx * width_cte],
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
