import numpy as np
from ultralytics import YOLO
import pandas as pd
from pathlib import Path
from typing import Optional, Tuple, Union
import logging

logger = logging.getLogger(__name__)


def read_label(label_filename: str, img: np.ndarray) -> Tuple[int, int, int, int]:
    """
    Read label file and extract bounding box coordinates.

    Args:
        label_filename (str): Path to the label file.
        img (np.ndarray): Corresponding image.

    Returns:
        Tuple[int, int, int, int]: Tuple containing center x, center y, width, and height of the bounding box.
    """
    label = pd.read_csv(label_filename, sep=" ", header=None)
    if label.shape[0] > 1:
        label = label.iloc[0]
    cx = int(label[1].iloc[0] * img.shape[1])
    cy = int(label[2].iloc[0] * img.shape[0])
    w = int(label[3].iloc[0] * img.shape[1])
    h = int(label[4].iloc[0] * img.shape[0])
    return cx, cy, w, h


def apd_dl(
    img_in: np.ndarray, output_dir: str, model_path: Union[str, str]
) -> Tuple[float, float]:
    """
    Adaptive Pith Detection using Deep Learning model.

    Args:
        img_in (np.ndarray): Input image.
        output_dir (str): Directory to save outputs.
        model_path (str or str): Path to the trained model weights.

    Returns:
        np.ndarray: Detected center point coordinates.
    """
    if model_path is None:
        raise ValueError("model_path is None")

    logger.info(f"model_path {model_path}")
    model = YOLO(model_path, task="detect")
    _ = model(img_in, project=output_dir, save=True, save_txt=True)
    label_path = Path(output_dir) / "predict/labels/image0.txt"
    cx, cy, _, _ = read_label(str(label_path), img_in)
    pith = (cx, cy)

    return pith
