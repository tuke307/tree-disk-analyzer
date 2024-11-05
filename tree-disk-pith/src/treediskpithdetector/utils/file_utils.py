import json
from pathlib import Path
import cv2
import shutil
from typing import Union, Dict
import numpy as np
import logging

logger = logging.getLogger(__name__)


def load_image(image_path: str) -> np.ndarray:
    """
    Loads an image from the given file path and converts it from BGR to RGB format.

    Args:
        image_path: Path to the image file.

    Returns:
        The image as a NumPy array in RGB format.
    """
    img = cv2.imread(image_path)
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


def save_image(image: np.ndarray, image_path: str) -> None:
    """
    Saves an image to the given file path.

    Args:
        image: The image to save.
        image_path: Path to save the image file.

    Returns:
        None
    """
    img_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    cv2.imwrite(image_path, img_bgr)


def load_json(filepath: Union[str, Path]) -> Dict:
    """
    Loads a JSON file and returns its contents as a dictionary.

    Args:
        filepath: Path to the JSON file.

    Returns:
        The loaded JSON data as a dictionary.

    Raises:
        FileNotFoundError: If the file does not exist.
        json.JSONDecodeError: If the file contains invalid JSON.
    """
    filepath = Path(filepath)

    if not filepath.is_file():
        raise FileNotFoundError(f"JSON file not found: {filepath}")
    with open(filepath, "r") as f:
        data = json.load(f)

    return data


def write_json(content: any, filepath: Union[str, Path]) -> None:
    """
    Writes a dictionary to a JSON file.

    Args:
        dict_to_save: Serializable dictionary to save.
        filepath: Path where to save the JSON file.

    Returns:
        None
    """
    filepath = Path(filepath)

    with open(filepath, "w") as f:
        json.dump(content, f, indent=4)


def clear_directory(directory: Path) -> None:
    """
    Clears all files and directories in the specified directory.

    Args:
        directory: The directory to clear.

    Returns:
        None

    Raises:
        FileNotFoundError: If the directory does not exist.
        PermissionError: If the program lacks permissions to modify the directory.
    """
    if not directory.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")

    for item in directory.iterdir():
        try:
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)
        except Exception as e:
            logger.error(f"Error deleting {item}: {e}")


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
