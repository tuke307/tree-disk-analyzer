import numpy as np
import cv2
from ultralytics import YOLO
import pandas as pd
from pathlib import Path
from typing import Optional, Tuple, Union
import logging

from ..geometry.structural_tensor import structural_tensor, sampling_structural_tensor
from ..optimization.optimizer import Optimization
from ..optimization.optimization_utils import filter_lo_around_c
from ..geometry.line_transformations import pclines_local_orientation_filtering
from ..optimization.least_squares_solver import LeastSquaresSolution
from ..utils.file_utils import save_image

logger = logging.getLogger(__name__)


def local_orientation(
    img_in: np.ndarray, st_sigma: float, st_window: int
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute the local orientation of an image using structural tensor.

    Args:
        img_in (np.ndarray): Input RGB image.
        st_sigma (float): Sigma value for Gaussian smoothing.
        st_window (int): Window size for the structural tensor.

    Returns:
        Tuple[np.ndarray, np.ndarray]: Tuple containing orientation tensor STo and coherence tensor STc.
    """
    gray_image = cv2.cvtColor(img_in, cv2.COLOR_RGB2GRAY).copy()
    STc, STo = structural_tensor(gray_image, sigma=st_sigma, window_size=st_window)
    return STo, STc


def lo_sampling(
    STo: np.ndarray,
    STc: np.ndarray,
    lo_w: int,
    percent_lo: float,
    debug: bool = False,
    img: Optional[np.ndarray] = None,
    output_folder: Optional[str] = None,
) -> np.ndarray:
    """
    Sample local orientations from the structural tensor.

    Args:
        STo (np.ndarray): Orientation tensor.
        STc (np.ndarray): Coherence tensor.
        lo_w (int): Window size for sampling.
        percent_lo (float): Percentage for thresholding high coherence orientations (0-1).
        debug (bool, optional): If True, debug images are saved. Defaults to False.
        img (np.ndarray, optional): Original image for visualization. Required if debug is True.
        output_folder (str, optional): Folder to save debug images. Required if debug is True.

    Returns:
        np.ndarray: Array of line segments representing local orientations.
    """
    STc, STo, kernel_size = sampling_structural_tensor(STc, STo, lo_w)

    # Get orientations with high coherence (above percent_lo)
    th = np.percentile(STc[STc > 0], 100 * (1 - percent_lo))
    y, x = np.where(STc > th)
    O = STo[y, x]

    # Convert orientations to vector (x1, y1, x2, y2)
    V = np.array([np.sin(O), np.cos(O)]).T
    orientation_length = kernel_size / 2
    Pc = np.array([x, y], dtype=float).T
    P1 = Pc - V * orientation_length / 2
    P2 = Pc + V * orientation_length / 2
    L = np.hstack((P1, P2))

    if debug:
        if img is None or output_folder is None:
            raise ValueError(
                "img and output_folder must be provided when debug is True."
            )
        img_s = img.copy()
        for x1, y1, x2, y2 in L:
            p1 = np.array((x1, y1), dtype=int)
            p2 = np.array((x2, y2), dtype=int)
            img_s = cv2.line(img_s, (p1[0], p1[1]), (p2[0], p2[1]), (0, 0, 255), 1)
            # Draw rectangle
            top = p1
            bottom = p2
            img_s = cv2.rectangle(
                img_s, (top[0], top[1]), (bottom[0], bottom[1]), (255, 0, 0), 1
            )

        path = str(Path(output_folder) / "img_end_s.png")
        save_image(img_s, path)
    return L


def pclines_postprocessing(
    img_in: np.ndarray,
    Lof: np.ndarray,
    ransac_outlier_th: float = 0.03,
    debug: bool = False,
    output_folder: Optional[str] = None,
) -> np.ndarray:
    """
    Perform PClines postprocessing on local orientations.

    Args:
        img_in (np.ndarray): Input image.
        Lof (np.ndarray): Local orientations array.
        ransac_outlier_th (float, optional): Outlier threshold for RANSAC. Defaults to 0.03.
        debug (bool, optional): If True, debug information is saved. Defaults to False.
        output_folder (str, optional): Folder to save debug outputs.

    Returns:
        np.ndarray: Processed local orientations.
    """
    m_lsd, _, _ = pclines_local_orientation_filtering(
        img_in,
        Lof,
        outlier_th=ransac_outlier_th,
        debug=debug,
        output_folder=output_folder,
    )
    return m_lsd


def optimization(
    img_in: np.ndarray,
    line_segments: np.ndarray,
    ci: Optional[Union[Tuple[float, float], np.ndarray]] = None,
) -> np.ndarray:
    """
    Perform optimization to find the pith (center point).

    Args:
        img_in (np.ndarray): Input image.
        line_segments (np.ndarray): Local orientations data.
        ci (Tuple[float, float] or np.ndarray, optional): Initial center point. If None, computed via least squares.

    Returns:
        np.ndarray: Optimized center point coordinates.
    """
    xo, yo = (
        LeastSquaresSolution(line_segments=line_segments, img=img_in).run()
        if ci is None
        else ci
    )
    pith = Optimization(line_segments=line_segments).run(xo, yo)
    pith = (pith[0], pith[1])

    return np.array(pith)


def pith_is_not_in_rectangular_region(
    ci_plus_1: Union[Tuple[float, float], np.ndarray],
    top_left: Union[Tuple[float, float], np.ndarray],
    bottom_right: Union[Tuple[float, float], np.ndarray],
) -> bool:
    """
    Check if the pith is outside a rectangular region defined by top-left and bottom-right corners.

    Args:
        ci_plus_1 (Tuple[float, float] or np.ndarray): The pith coordinates.
        top_left (Tuple[float, float] or np.ndarray): Top-left corner of the rectangle.
        bottom_right (Tuple[float, float] or np.ndarray): Bottom-right corner of the rectangle.

    Returns:
        bool: True if pith is outside the rectangle, False otherwise.
    """
    x, y = ci_plus_1
    return (
        x < top_left[0] or y < top_left[1] or x > bottom_right[0] or y > bottom_right[1]
    )


def apd(
    img_in: np.ndarray,
    st_sigma: float,
    st_window: int,
    lo_w: int,
    percent_lo: float,
    max_iter: int,
    rf: float,
    epsilon: float,
    pclines: bool = False,
    debug: bool = False,
    output_dir: Optional[Path] = None,
) -> np.ndarray:
    """
    Adaptive Pith Detection (APD) algorithm.

    Args:
        img_in (np.ndarray): Input image.
        st_sigma (float): Sigma for structural tensor.
        st_window (int): Window size for structural tensor.
        lo_w (int): Window size for local orientation sampling.
        percent_lo (float): Percentage for thresholding high coherence orientations (0-1).
        max_iter (int): Maximum number of iterations.
        rf (float): Radius factor for filtering orientations around center point.
        epsilon (float): Convergence threshold.
        pclines (bool, optional): If True, use PClines postprocessing. Defaults to False.
        debug (bool, optional): If True, debug information is saved. Defaults to False.
        output_dir (Path, optional): Directory to save outputs.

    Returns:
        np.ndarray: Detected center point coordinates.
    """
    STo, STc = local_orientation(img_in, st_sigma=st_sigma, st_window=st_window)

    Lof = lo_sampling(
        STo, STc, lo_w, percent_lo, debug=debug, img=img_in, output_folder=output_dir
    )

    if pclines:
        Lof = pclines_postprocessing(img_in, Lof, debug=debug, output_folder=output_dir)

    ci = None
    for i in range(max_iter):
        if i > 0:
            Lor, top_left, bottom_right = filter_lo_around_c(Lof, rf, ci, img_in)
        else:
            Lor = Lof

        ci_plus_1 = optimization(img_in, Lor, ci)

        if i > 0:
            if np.linalg.norm(ci_plus_1 - ci) < epsilon:
                ci = ci_plus_1
                break

            if pith_is_not_in_rectangular_region(ci_plus_1, top_left, bottom_right):
                break

        ci = ci_plus_1

    return ci


def apd_pcl(
    img_in: np.ndarray,
    st_sigma: float,
    st_window: int,
    lo_w: int,
    percent_lo: float,
    max_iter: int,
    rf: float,
    epsilon: float,
    debug: bool = False,
    output_dir: Optional[Path] = None,
) -> np.ndarray:
    """
    Adaptive Pith Detection using PClines postprocessing.

    Args:
        img_in (np.ndarray): Input image.
        st_sigma (float): Sigma for structural tensor.
        st_window (int): Window size for structural tensor.
        lo_w (int): Window size for local orientation sampling.
        percent_lo (float): Percentage for thresholding high coherence orientations (0-1).
        max_iter (int): Maximum number of iterations.
        rf (float): Radius factor for filtering orientations around center point.
        epsilon (float): Convergence threshold.
        debug (bool, optional): If True, debug information is saved. Defaults to False.
        output_dir (Path, optional): Directory to save outputs.

    Returns:
        np.ndarray: Detected center point coordinates.
    """
    pith = apd(
        img_in,
        st_sigma,
        st_window,
        lo_w,
        percent_lo,
        max_iter,
        rf,
        epsilon,
        pclines=True,
        debug=debug,
        output_dir=output_dir,
    )
    return pith


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
) -> np.ndarray:
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
    pith = np.array([cx, cy])

    return pith
