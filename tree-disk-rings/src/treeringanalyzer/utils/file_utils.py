import os
import json
from pathlib import Path
import cv2
import shutil
from pathlib import Path
from typing import List, Any, Tuple, Dict
import numpy as np

from .geometry.curve import Curve
from .geometry.chain import Chain, TypeChains
from .geometry.geometry_utils import visualize_chains_over_image
from .processing.preprocessing import resize


def save_config(args: dict, root_path: str, output_dir: str) -> int:
    """
    Save configuration to disk.

    Args:
        args (dict): Arguments from the command line.
        root_path (str): Root path.
        output_dir (str): Output directory.

    Returns:
        int: 0 if successful.
    """
    config = load_config()

    config["result_path"] = output_dir

    if "nr" in args and args["nr"]:
        config["nr"] = args["nr"]

    if "height" in args and "width" in args:
        if args["height"] > 0 and args["width"] > 0:
            config["resize"] = [args["height"], args["width"]]

    if "min_chain_length" in args and args["min_chain_length"]:
        config["min_chain_length"] = args["min_chain_length"]

    if "alpha" in args and args["alpha"]:
        config["edge_th"] = args["alpha"]

    if "sigma" in args and args["sigma"]:
        config["sigma"] = args["sigma"]

    if "th_high" in args and args["th_high"]:
        config["th_high"] = args["th_high"]

    if "th_low" in args and args["th_low"]:
        config["th_low"] = args["th_low"]

    if "debug" in args and args["debug"]:
        config["debug"] = True

    config["devernay_path"] = str(Path(root_path) / "externas/devernay_1.0")

    write_json(config, Path(root_path) / "config/general.json")

    return 0


def saving_results(
    res: Tuple[
        np.ndarray,
        np.ndarray,
        np.ndarray,
        List[Curve],
        List[Chain],
        List[Chain],
        List[Chain],
        Dict[str, Any],
    ],
    output_dir: str,
    save_imgs=True,
) -> None:
    """
    Save the results of the tree ring detection algorithm to disk.

    Args:
        res (Tuple): Tuple with the results of the tree ring detection algorithm.
        output_dir (str): Output directory.
        save_imgs (bool, optional): Flag to save images. Defaults to True.

    Returns:
        None
    """
    im_seg, im_pre, ch_e, ch_f, ch_s, ch_c, ch_p, labelme_json = res

    write_json(labelme_json, f"{output_dir}/labelme.json")

    if not save_imgs:
        return

    m, n, _ = im_seg.shape
    m_n, n_n = im_pre.shape

    if m != m_n:
        im_seg, _, _ = resize(im_seg, m_n, n_n)

    visualize_chains_over_image(img=im_seg, filename=f"{output_dir}/segmentation.png")
    visualize_chains_over_image(img=im_pre, filename=f"{output_dir}/preprocessing.png")
    visualize_chains_over_image(
        img=im_pre, filename=f"{output_dir}/edges.png", devernay=ch_e
    )
    visualize_chains_over_image(
        img=im_pre, filename=f"{output_dir}/filter.png", filter=ch_f
    )
    visualize_chains_over_image(
        chain_list=ch_s, img=im_seg, filename=f"{output_dir}/chains.png"
    )
    visualize_chains_over_image(
        chain_list=ch_c, img=im_seg, filename=f"{output_dir}/connect.png"
    )
    visualize_chains_over_image(
        chain_list=ch_p, img=im_seg, filename=f"{output_dir}/postprocessing.png"
    )
    visualize_chains_over_image(
        chain_list=[
            chain
            for chain in ch_p
            if chain.is_closed()
            and chain.type not in [TypeChains.center, TypeChains.border]
        ],
        img=im_seg,
        filename=f"{output_dir}/output.png",
    )

    return


def chain_2_labelme_json(
    chain_list: List[Chain],
    image_height: int,
    image_width: int,
    cy: int,
    cx: int,
    img_orig: np.ndarray,
    image_path: str,
    exec_time: float,
) -> Dict[str, Any]:
    """
    Converting ch_i list object to labelme format. This format is used to store the coordinates of the rings at the image
    original resolution

     Args:
        chain_list (List[Chain]): List of chains.
        image_height (int): Image height.
        image_width (int): Image width.
        cy (int): Pith y's coordinate.
        cx (int): Pith x's coordinate.
        img_orig (np.ndarray): Original image.
        image_path (str): Image input path.
        exec_time (float): Method execution time.

    Returns:
        Dict[str, Any]: JSON in labelme format. Ring coordinates are stored here.
    """
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
        "imageHeight": None,
        "imageWidth": None,
        "version": "5.5.0",
        "flags": {},
        "shapes": [],
        "imageData": None,
        "exec_time(s)": exec_time,
        "center": [cy * height_cte, cx * width_cte],
    }
    for idx, chain in enumerate(completed_chains):
        ring = {"label": str(idx + 1)}
        ring["points"] = [
            [node.x * width_cte, node.y * height_cte] for node in chain.l_nodes
        ]
        ring["shape_type"] = "polygon"
        ring["flags"] = {}
        labelme_json["shapes"].append(ring)

    return labelme_json


def load_image(filename: str) -> np.ndarray:
    """
    Load image utility.

    Args:
        filename (str): Path to image file.

    Returns:
        np.ndarray: Image as a numpy array.
    """
    img = cv2.imread(filename)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    return img


def load_config(default: bool = True) -> dict:
    """
    Load configuration utility.

    Args:
        default (bool, optional): Load default configuration. Defaults to True.

    Returns:
        dict: configuration as a dictionary
    """
    dir_path = os.path.dirname(os.path.realpath(__file__))

    return (
        load_json(f"{dir_path}/../../config/default.json")
        if default
        else load_json(f"{dir_path}/../../config/general.json")
    )


def load_json(filepath: str) -> dict:
    """
    Load json file utility.

    Args:
        filepath (str): path to json file

    Returns:
        dict: json file as a dictionary
    """
    with open(str(filepath), "r") as f:
        data = json.load(f)

    return data


def write_json(dict_to_save: dict, filepath: str) -> None:
    """
    Write json file utility.

    Args:
        dict_to_save (dict): dictionary to save
        filepath (str): path to save json file

    Returns:
        None
    """
    with open(str(filepath), "w") as f:
        json.dump(dict_to_save, f)


def clear_dir(dir: str) -> None:
    """
    Clear directory utility.

    Args:
        dir (str): directory to clear

    Returns:
        None
    """
    dir = Path(dir)

    for item in dir.iterdir():
        if item.is_file():
            item.unlink()
        elif item.is_dir():
            shutil.rmtree(item)
