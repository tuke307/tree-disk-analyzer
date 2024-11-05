import json
import shutil
from pathlib import Path
from typing import Dict, Any
import cv2
import numpy as np


def clear_directory(dir_path: Path) -> None:
    """
    Clear all contents of a directory.

    Args:
        dir_path (Path): Directory to clear
    """
    if not dir_path.exists():
        return

    for item in dir_path.iterdir():
        if item.is_file():
            item.unlink()
        elif item.is_dir():
            shutil.rmtree(item)


def load_json(filepath: Path) -> dict:
    """
    Load a JSON file.

    Args:
        filepath (Path): Path to JSON file

    Returns:
        dict: Loaded JSON data
    """
    with filepath.open("r") as f:
        return json.load(f)


def write_json(data: Dict[str, Any], filepath: Path) -> None:
    """
    Write data to a JSON file.

    Args:
        data (Dict[str, Any]): Data to write
        filepath (Path): Output file path
    """
    with open(filepath, "w") as f:
        json.dump(data, f, indent=4)


def load_image(filepath: Path) -> cv2.typing.MatLike:
    """
    Load an image file.

    Args:
        filepath (Path): Path to image file

    Returns:
        cv2.typing.MatLike: Image as RGB numpy array
    """
    img = cv2.imread(str(filepath))
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


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
