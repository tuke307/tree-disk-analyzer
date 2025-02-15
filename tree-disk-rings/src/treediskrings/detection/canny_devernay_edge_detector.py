import os
from pathlib import Path
from typing import Dict, List, Tuple
from venv import logger

import cv2
import numpy as np
import pandas as pd
from importlib import resources
import platform

from ..config import config


def get_architecture() -> str:
    machine = platform.machine().lower()
    if machine.startswith("arm") or "aarch" in machine:
        return "arm64"
    elif machine in ("amd64", "x86_64"):
        return "x86_64"
    else:
        return "unknown"


def get_platform() -> str:
    system = platform.system().lower()
    if system == "linux":
        return "linux"
    elif system == "darwin":
        return "macos"
    elif system == "windows":
        return "windows"
    else:
        return "Unknown"


def get_devernay_path() -> str:
    """Get the absolute path to the appropriate devernay binary based on the platform."""
    base_package = "treediskrings.externals"

    # Determine subdirectory and binary name based on platform
    platform = get_platform()
    architecture = get_architecture()

    if platform == "linux":
        if architecture == "x86_64":
            subdir = "linux-x86_64"
            binary_name = "devernay.out"
        elif architecture == "arm64":
            subdir = "linux-arm"
            binary_name = "devernay.out"
        else:
            raise ValueError(f"Unsupported architecture: {architecture}")
    elif platform == "macos":
        if architecture == "x86_64":
            NotImplementedError(f"macOS x86_64 is not supported")
        elif architecture == "arm64":
            subdir = "macos-arm64"
            binary_name = "devernay.out"
        else:
            raise ValueError(f"Unsupported architecture: {architecture}")
    elif platform == "windows":
        raise NotImplementedError("Windows is not supported")
    else:
        raise ValueError(f"Unsupported platform: {platform}")

    # Construct the path to the binary using the resources API
    binary_path = resources.files(base_package) / subdir / binary_name
    binary_path = str(binary_path)

    # Ensure the file exists
    if not os.path.isfile(binary_path):
        raise FileNotFoundError(f"Binary not found at {binary_path}")

    # Make sure it's executable (skip on Windows)
    if platform != "windows":
        os.chmod(binary_path, 0o755)

    return binary_path


def load_curves(output_txt: Path) -> np.ndarray:
    """
    Loads curves from a text file.

    Args:
        output_txt (str): Path to the output text file containing curves.

    Returns:
        np.ndarray: Array of curves loaded from the file.
    """
    curves_list = pd.read_csv(output_txt, delimiter=" ", header=None).values
    return curves_list


def convert_image_to_pgm(img_pre: np.ndarray) -> Path:
    """
    Converts an image to PGM format and saves it.

    Args:
        img_pre (np.ndarray): Preprocessed image array.

    Returns:
        str: Path to the saved image file.
    """
    image_path = Path(config.output_dir) / "test.pgm"
    cv2.imwrite(str(image_path), img_pre)

    return image_path


def delete_files(files: List[Path]) -> None:
    """
    Deletes a list of files.

    Args:
        files (List[Path]): List of file paths to delete.
    """
    for file in files:
        os.system(f"rm {file}")


def gradient_load(
    img: np.ndarray, gx_path: str, gy_path: str
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Loads gradient images from files.

    Args:
        img (np.ndarray): Original image array for size reference.
        gx_path (str): Path to the gradient X file.
        gy_path (str): Path to the gradient Y file.

    Returns:
        Tuple[np.ndarray, np.ndarray]: Gradient images Gx and Gy.
    """
    Gx = np.zeros_like(img, dtype=float)
    Gy = np.zeros_like(img, dtype=float)
    Gx[1:-1, 1:-1] = pd.read_csv(gx_path, delimiter=" ", header=None).values.T
    Gy[1:-1, 1:-1] = pd.read_csv(gy_path, delimiter=" ", header=None).values.T

    return Gx, Gy


def execute_command(
    image_path: Path, sigma: float, low: float, high: float
) -> Tuple[Path, Path, Path]:
    """
    Executes the Devernay edge detector command.

    Args:
        image_path (Path): Path to the image file.
        sigma (float): Gaussian filter sigma value.
        low (float): Low threshold for edge detection.
        high (float): High threshold for edge detection.

    Returns:
        Tuple[Path, Path, Path]: Paths to the gradient X, gradient Y, and output text files.
    """
    output_txt = Path(config.output_dir) / "output.txt"
    gx_path = Path(config.output_dir) / "gx.txt"
    gy_path = Path(config.output_dir) / "gy.txt"
    devernay_path = get_devernay_path()
    command = (
        f"{devernay_path} {image_path} -s {sigma} -l {low} -h {high} "
        f"-t {output_txt} -x {gx_path} -y {gy_path}"
    )
    os.system(command)
    return gx_path, gy_path, output_txt


def canny_deverney_edge_detector(
    img_pre: np.ndarray, sigma: float, low: float, high: float
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Canny edge detector module using the Canny/Devernay algorithm.
    Downloaded from https://doi.org/10.5201/ipol.2017.216

    Args:
        img_pre (np.ndarray): Preprocessed image.
        sigma (float): Gaussian filter sigma value for edge detection.
        low (float): Low gradient threshold.
        high (float): High gradient threshold.

     Returns:
        Tuple[np.ndarray, np.ndarray, np.ndarray]:
            A tuple containing:
            - m_ch_e (np.ndarray): Devernay curves.
            - Gx (np.ndarray): Gradient image in the x direction.
            - Gy (np.ndarray): Gradient image in the y direction.
    """
    im_path = convert_image_to_pgm(img_pre)
    gx_path, gy_path, output_txt = execute_command(im_path, sigma, low, high)
    Gx, Gy = gradient_load(img_pre, str(gx_path), str(gy_path))
    m_ch_e = load_curves(output_txt)
    delete_files([output_txt, im_path, gx_path, gy_path])

    return m_ch_e, Gx, Gy
