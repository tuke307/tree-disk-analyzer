from typing import Tuple, Optional, List, Union
import numpy as np
import cv2
from pathlib import Path
from skimage.util.shape import view_as_windows
from ..utils.file_utils import save_image


def structural_tensor(
    img: np.ndarray, sigma: float = 1.0, window_size: int = 5, mode: int = -1
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute the structural tensor of an image.

    Args:
        img (np.ndarray): Input grayscale image.
        sigma (float): Sigma of the Gaussian filter.
        window_size (int): Size of the window used to compute the structural tensor.
        mode (int): Gradient operator to use.
            -1 for Scharr operator,
            Positive odd integers (e.g., 3, 5, 7) for Sobel operator kernel size.

    Returns:
        Tuple[np.ndarray, np.ndarray]: Coherency and orientation matrices.
    """
    img = img.astype(np.float32)
    img = cv2.GaussianBlur(img, (3, 3), sigma)

    if mode == -1:
        # Use Scharr operator
        Ix = cv2.Scharr(img, cv2.CV_64F, 1, 0)
        Iy = cv2.Scharr(img, cv2.CV_64F, 0, 1)
    else:
        # Use Sobel operator with specified kernel size
        if mode % 2 == 1 and mode > 0:
            ksize = mode
        else:
            raise ValueError(
                "mode must be -1 for Scharr or a positive odd integer for Sobel kernel size."
            )
        Ix = cv2.Sobel(img, cv2.CV_64F, 1, 0, ksize=ksize)
        Iy = cv2.Sobel(img, cv2.CV_64F, 0, 1, ksize=ksize)

    J11 = Ix**2
    J22 = Iy**2
    J12 = Ix * Iy

    # Smooth the components of the structure tensor
    for J in (J11, J22, J12):
        cv2.GaussianBlur(J, (window_size, window_size), sigma, dst=J)

    # Compute eigenvalues
    tmp1 = J11 + J22
    tmp2 = cv2.multiply(J11 - J22, J11 - J22)
    tmp3 = cv2.multiply(J12, J12)
    tmp4 = np.sqrt(tmp2 + 4.0 * tmp3)

    lambda1 = 0.5 * (tmp1 + tmp4)  # Largest eigenvalue
    lambda2 = 0.5 * (tmp1 - tmp4)  # Smallest eigenvalue

    # Compute coherency and orientation
    imgCoherencyOut = cv2.divide(lambda1 - lambda2, lambda1 + lambda2)
    imgOrientationOut = 0.5 * cv2.phase(J22 - J11, 2.0 * J12, angleInDegrees=False)

    return imgCoherencyOut, imgOrientationOut


def sampling_structural_tensor(
    imgC: np.ndarray, imgO: np.ndarray, kernel_size: int
) -> Tuple[np.ndarray, np.ndarray, int]:
    """
    Sample structural tensor using sliding windows.

    Args:
        imgC: Coherency matrix
        imgO: Orientation matrix
        kernel_size: Size of the sliding window

    Returns:
        Tuple containing the sampled coherency and orientation matrices
    """
    img_h, img_w = imgC.shape
    imgO_out, imgC_output = imgO.copy(), np.zeros_like(imgC)

    windows_img_4d = view_as_windows(imgC, (kernel_size, kernel_size), step=kernel_size)
    windows_img_matrix = windows_img_4d.reshape(-1, kernel_size * kernel_size)

    argmax = np.argmax(windows_img_matrix, axis=1)
    windows_col = img_w // kernel_size

    windows_index = np.arange(len(argmax))
    upper_windows_row = (windows_index // windows_col) * kernel_size
    max_window_row = upper_windows_row + (argmax % kernel_size)
    max_window_col = (argmax // kernel_size) + (
        windows_index % windows_col
    ) * kernel_size

    max_loc = np.vstack((max_window_row, max_window_col)).T
    imgC_output[max_loc[:, 0], max_loc[:, 1]] = imgC[max_loc[:, 0], max_loc[:, 1]]

    return imgC_output, imgO_out, kernel_size


def matrix_compute_local_orientation(
    img: np.ndarray,
    W: int = 35,
    Sigma: float = 1.2,
    C_threshold: float = 0.75,
    ST_window: int = 100,
    debug: bool = False,
    output_folder: Optional[Path] = None,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute local orientation using matrix operations.

    Args:
        img: Input image
        W: Size of the window used to compute the structural tensor
        Sigma: Sigma of the gaussian filter
        C_threshold: Coherence threshold
        ST_window: Size of the sliding window
        debug: Debug flag
        output_folder: Output folder

    Returns:
        Tuple containing lines array and coherence array
    """
    gray_image = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY).copy()
    imgC, imgO = structural_tensor(gray_image, window_size=W, sigma=Sigma)

    imgC, imgO, kernel_size = (
        sampling_structural_tensor(imgC, imgO, ST_window)
        if ST_window > 0
        else (imgC, imgO, W)
    )

    th = np.percentile(imgC[imgC > 0], 100 * (1 - C_threshold))
    y, x = np.where(imgC > th)
    O = imgO[y, x]

    V = np.array([np.sin(O), np.cos(O)]).T
    orientation_length = kernel_size / 2
    Pc = np.array([x, y], dtype=float).T
    P1 = Pc - V * orientation_length / 2
    P2 = Pc + V * orientation_length / 2

    L = np.hstack((P1, P2))
    coherence = imgC[y, x]

    if debug and output_folder:
        _draw_debug_visualization(img, L, output_folder)

    return L, coherence


def _draw_debug_visualization(
    img: np.ndarray, L: np.ndarray, output_folder: Path
) -> None:
    """Helper function to draw debug visualization."""
    img_s = img.copy()
    for x1, y1, x2, y2 in L:
        p1 = np.array((x1, y1), dtype=int)
        p2 = np.array((x2, y2), dtype=int)
        cv2.line(img_s, (p1[0], p1[1]), (p2[0], p2[1]), (0, 0, 255), 1)
        cv2.rectangle(img_s, (p1[0], p1[1]), (p2[0], p2[1]), (255, 0, 0), 1)

    path = str(Path(output_folder) / "img_end_s.png")
    save_image(img_s, path)
