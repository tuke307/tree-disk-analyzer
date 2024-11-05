import json
from pathlib import Path
import cv2
import shutil
from pathlib import Path
import numpy as np


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


def save_image(filename: str, result_image: np.ndarray) -> None:
    """
    Save the final image after removing the salient object.

    Args:
        filename (str): Path to save the output image.
        result_image (np.ndarray): The result image with the background set to white.

    Returns:
        None
    """
    # Convert to BGR if needed
    result_image_bgr = cv2.cvtColor(result_image, cv2.COLOR_RGB2BGR)
    cv2.imwrite(filename, result_image_bgr)


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


def clear_directory(dir: str) -> None:
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


def ensure_directory(dir_path: Path, clear: bool = False) -> Path:
    """
    Ensure a directory exists, optionally clearing it first.

    Args:
        dir_path (Path): Directory path
        clear (bool): Whether to clear existing contents

    Returns:
        Path: Resolved directory path
    """
    dir_path = dir_path.resolve()

    if dir_path.exists() and clear:
        clear_directory(dir_path)

    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path
