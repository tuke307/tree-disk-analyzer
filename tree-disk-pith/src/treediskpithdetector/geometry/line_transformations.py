import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Tuple, Optional, List

from ..visualization.drawing import Shapes, LineDrawing


def pclines_straight_all(
    l: np.ndarray, d: float = 1.0
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Computes the (u, v) coordinates in the straight TS-space for all lines.

    Args:
        l: An array of shape (n_lines, 4), where each row represents a line as [x1, y1, x2, y2].
        d: A float parameter used in the transformation.

    Returns:
        A tuple (u, v), where u and v are arrays of coordinates in the TS-space.
    """
    x1 = l[:, 0]
    y1 = l[:, 1]
    x2 = l[:, 2]
    y2 = l[:, 3]

    dy = y2 - y1
    dx = x2 - x1

    # Handle vertical lines where dx == 0
    with np.errstate(divide="ignore", invalid="ignore"):
        m = np.divide(dy, dx)
        b = np.divide(y1 * x2 - y2 * x1, dx)

    # For vertical lines, set m to a large number and b to NaN
    m[np.isinf(m)] = np.inf
    b[np.isnan(b)] = np.nan

    # Compute homogeneous coordinates
    PCline = np.column_stack((np.full(b.shape, d), b, 1 - m))

    # Avoid division by zero
    with np.errstate(divide="ignore", invalid="ignore"):
        u = PCline[:, 0] / PCline[:, 2]
        v = PCline[:, 1] / PCline[:, 2]

    return u, v


def pclines_twisted_all(l: np.ndarray, d: float = 1.0) -> Tuple[np.ndarray, np.ndarray]:
    """
    Computes the (u, v) coordinates in the twisted TS-space for all lines.

    Args:
        l: An array of shape (n_lines, 4), where each row represents a line as [x1, y1, x2, y2].
        d: A float parameter used in the transformation.

    Returns:
        A tuple (u, v), where u and v are arrays of coordinates in the TS-space.
    """
    x1 = l[:, 0]
    y1 = l[:, 1]
    x2 = l[:, 2]
    y2 = l[:, 3]

    dy = y2 - y1
    dx = x2 - x1

    # Handle vertical lines where dx == 0
    with np.errstate(divide="ignore", invalid="ignore"):
        m = np.divide(dy, dx)
        b = np.divide(y1 * x2 - y2 * x1, dx)

    # For vertical lines, set m to a large number and b to NaN
    m[np.isinf(m)] = np.inf
    b[np.isnan(b)] = np.nan

    # Compute homogeneous coordinates
    PCline = np.column_stack((-np.full(b.shape, d), -b, 1 + m))

    # Avoid division by zero
    with np.errstate(divide="ignore", invalid="ignore"):
        u = PCline[:, 0] / PCline[:, 2]
        v = PCline[:, 1] / PCline[:, 2]

    return u, v


def ts_space(
    img: np.ndarray,
    lines: np.ndarray,
    output_dir: str,
    d: float = 1.0,
    debug: bool = True,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Transforms lines into TS-space coordinates for both straight and twisted spaces.

    Args:
        img: The input image array.
        lines: An array of lines with shape (n_lines, 4).
        output_dir: Directory to save debug plots.
        d: Parameter used in the transformation.
        debug: Whether to save debug plots.

    Returns:
        points_straight: TS-space points in the straight space.
        points_twisted: TS-space points in the twisted space.
        lines_straight: Lines corresponding to points in the straight space.
        lines_twisted: Lines corresponding to points in the twisted space.
    """
    H, W = img.shape[:2]
    v_maximum = max(W / 2, H / 2)
    l_lo = lines.reshape(-1, 4)
    l_lo_norm = l_lo / np.array([W, H, W, H])

    u_straight, v_straight = pclines_straight_all(l_lo_norm, d=d)
    points_straight = np.vstack((u_straight, v_straight)).T

    u_twisted, v_twisted = pclines_twisted_all(l_lo_norm, d=d)
    points_twisted = np.vstack((u_twisted, v_twisted)).T

    # Impose boundaries of pclines space
    mask_straight = (
        (points_straight[:, 0] >= 0)
        & (points_straight[:, 0] <= d)
        & (points_straight[:, 1] >= -v_maximum)
        & (points_straight[:, 1] <= v_maximum)
    )

    points_straight = points_straight[mask_straight]
    lines_straight = l_lo[mask_straight]

    mask_twisted = (
        (points_twisted[:, 0] >= -d)
        & (points_twisted[:, 0] <= 0)
        & (points_twisted[:, 1] >= -v_maximum)
        & (points_twisted[:, 1] <= v_maximum)
    )

    points_twisted = points_twisted[mask_twisted]
    lines_twisted = l_lo[mask_twisted]

    if debug:
        fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(14, 7))
        axes[0].scatter(points_twisted[:, 0], points_twisted[:, 1], s=0.1)
        axes[1].scatter(points_straight[:, 0], points_straight[:, 1], s=0.1)
        axes[0].set_title("Twisted Space")
        axes[1].set_title("Straight Space")
        axes[0].set_xlabel("u")
        axes[0].set_ylabel("v")
        axes[1].set_xlabel("u")
        axes[1].set_ylabel("v")
        axes[0].grid(True)
        axes[1].grid(True)
        plt.tight_layout()
        plt.savefig(f"{output_dir}/pc_m_b_representation_ts_space_subplots.png")
        plt.close()

    return points_straight, points_twisted, lines_straight, lines_twisted


def robust_line_estimation(
    X: np.ndarray, y: np.ndarray, residual_threshold: float = 0.03
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Estimates a robust line fit to the data using RANSAC.

    Args:
        X: Independent variable data as a 1D array.
        y: Dependent variable data as a 1D array.
        residual_threshold: Threshold for determining inliers.

    Returns:
        line: Array containing the coefficient and bias of the line [coefficient, bias].
        residuals: Array of residuals for each data point.
    """
    from sklearn.linear_model import RANSACRegressor

    X = X.flatten()
    y = y.flatten()

    min_samples = max(100, int(round(X.shape[0] * 0.05)))
    min_samples = min(min_samples, X.shape[0])
    ransac = RANSACRegressor(
        min_samples=min_samples,
        max_trials=1000,
        residual_threshold=residual_threshold,
        random_state=42,
    )
    try:
        ransac.fit(X.reshape(-1, 1), y.reshape(-1, 1))
    except ValueError:
        return np.array([0, 0]), np.full(X.shape[0], np.inf)

    coefficient = ransac.estimator_.coef_[0][0]
    bias = ransac.estimator_.intercept_[0]
    line = np.array([coefficient, bias])
    residuals = np.abs(coefficient * X + bias - y)

    return line, residuals


def find_detections(
    points: np.ndarray,
    output_path: str,
    debug: bool = False,
    outliers_threshold: float = 0.1,
    alineation_threshold: float = 0.45,
) -> Tuple[np.ndarray, Optional[float], Optional[float], np.ndarray, bool]:
    """
    Finds inlier points that align along a line using robust estimation.

    Args:
        points: Array of points in TS-space.
        output_path: Path to save debug plots.
        debug: Whether to save debug plots.
        outliers_threshold: Residual threshold for inliers.
        alineation_threshold: Threshold for considering good alignment.

    Returns:
        inliers: Indices of inlier points.
        line_slope: Slope of the estimated line.
        line_bias: Bias of the estimated line.
        residuals: Residuals of the inlier points.
        good_alignment: Whether the alignment is considered good.
    """
    v = points[:, 1]
    u = points[:, 0]

    if v.size < 2:
        return np.array([], dtype=int), None, None, np.array([]), False

    line, residuals = robust_line_estimation(
        u, v, residual_threshold=outliers_threshold
    )
    inliers = np.where(residuals <= outliers_threshold)[0]

    p90 = np.percentile(residuals, 99)
    good_alignment = p90 < alineation_threshold

    if debug:
        plt.figure()
        plt.scatter(u, v, s=0.1, c="b", label="Data")
        plt.scatter(u[inliers], v[inliers], s=0.1, c="g", label="Inliers")
        plt.plot(u, line[0] * u + line[1], color="red", label="Line estimation")
        plt.legend(loc="lower right")
        plt.xlabel("u")
        plt.ylabel("v")
        plt.savefig(output_path)
        plt.close()

    return inliers, line[0], line[1], residuals[inliers], good_alignment


def get_duplicated_elements_in_array(arr: np.ndarray) -> np.ndarray:
    """
    Finds duplicated rows in a 2D array.

    Args:
        arr: A 2D NumPy array.

    Returns:
        An array of duplicated rows.
    """
    unique_rows, counts = np.unique(arr, axis=0, return_counts=True)
    duplicated_rows = unique_rows[counts > 1]
    return duplicated_rows


def get_indexes_relative_to_src_list_if_there_is_more_than_one(
    src_array: np.ndarray, dst_array: np.ndarray
) -> List[int]:
    """
    Gets indexes of src_array in dst_array when there are duplicates.

    Args:
        src_array: 2D array to search for in dst_array.
        dst_array: 2D array where src_array is searched.

    Returns:
        List of indices in dst_array where elements of src_array are found.
    """
    idx = []
    for i in range(src_array.shape[0]):
        indexes = np.where((dst_array == src_array[i]).all(axis=1))[0][:-1].tolist()
        idx.extend(indexes)
    return idx


def get_converging_lines_pc(
    img: np.ndarray,
    m_lsd: np.ndarray,
    coherence: Optional[np.ndarray],
    output_dir: Optional[str],
    outlier_th: float = 0.05,
    debug: bool = False,
) -> Tuple[np.ndarray, np.ndarray, Optional[np.ndarray], bool]:
    """
    Identifies converging lines in the image using TS-space.

    Args:
        img: The input image array.
        m_lsd: Array of line segments.
        coherence: Optional array of coherence values.
        output_dir: Directory to save debug outputs.
        outlier_th: Residual threshold for inliers.
        debug: Whether to save debug outputs.

    Returns:
        converging_lines: Array of converging line segments.
        idx_lines: Indices of the converging lines in m_lsd.
        coherence: Coherence values for the converging lines.
        good_alignment: Whether the alignment is considered good.
    """
    if output_dir is not None:
        vp_output_dir = Path(output_dir)
        vp_output_dir.mkdir(parents=True, exist_ok=True)
    else:
        vp_output_dir = Path(".")

    m_pc_straight, m_pc_twisted, m_img_straight, m_img_twisted = ts_space(
        img, m_lsd, output_dir=str(vp_output_dir), d=1, debug=debug
    )

    idx_inliers_straight, m1, b1, residual_straight, alineation_st = find_detections(
        m_pc_straight,
        output_path=f"{vp_output_dir}/ts_straight.png",
        outliers_threshold=outlier_th,
        debug=debug,
    )

    idx_inliers_twisted, m2, b2, residual_twisted, alineation_tw = find_detections(
        m_pc_twisted,
        output_path=f"{vp_output_dir}/ts_twisted.png",
        outliers_threshold=outlier_th,
        debug=debug,
    )

    if debug:
        LineDrawing.draw_lsd_lines(
            m_lsd, img, output_path=f"{vp_output_dir}/lsd.png", lines_all=m_lsd
        )

        LineDrawing.draw_lsd_lines(
            m_img_straight[idx_inliers_straight],
            img,
            output_path=f"{vp_output_dir}/straight_lines_in_image.png",
            lines_all=m_lsd,
        )

        LineDrawing.draw_lsd_lines(
            m_img_twisted[idx_inliers_twisted],
            img,
            output_path=f"{vp_output_dir}/twisted_lines_in_image.png",
            lines_all=m_lsd,
        )

    converging_lines = np.vstack(
        (m_img_straight[idx_inliers_straight], m_img_twisted[idx_inliers_twisted])
    )
    residuals = np.concatenate((residual_straight, residual_twisted))
    if coherence is not None:
        coherence = np.concatenate(
            (coherence[idx_inliers_straight], coherence[idx_inliers_twisted])
        )
    idx_lines = np.concatenate((idx_inliers_straight, idx_inliers_twisted))

    duplicated_lines = get_duplicated_elements_in_array(converging_lines)
    idx_duplicated_lines = get_indexes_relative_to_src_list_if_there_is_more_than_one(
        duplicated_lines, converging_lines
    )
    converging_lines = np.delete(converging_lines, idx_duplicated_lines, axis=0)
    residuals = np.delete(residuals, idx_duplicated_lines, axis=0)
    if coherence is not None:
        coherence = np.delete(coherence, idx_duplicated_lines, axis=0)
    idx_lines = np.delete(idx_lines, idx_duplicated_lines, axis=0)

    if debug:
        LineDrawing.draw_lsd_lines(
            converging_lines,
            img,
            output_path=f"{vp_output_dir}/converging_segment_in_image.png",
            lines_all=m_lsd,
        )

        LineDrawing.draw_lines(
            converging_lines,
            img,
            output_path=f"{vp_output_dir}/converging_lo_in_image.png",
        )

    return converging_lines, idx_lines, coherence, alineation_st and alineation_tw


def rotate_lines(L: np.ndarray, degrees: float = 90.0) -> np.ndarray:
    """
    Rotates lines by a specified angle.

    Args:
        L: Array of lines with shape (n_lines, 4).
        degrees: Angle in degrees to rotate the lines.

    Returns:
        Rotated lines as an array of shape (n_lines, 4).
    """
    X1, Y1, X2, Y2 = L[:, 0], L[:, 1], L[:, 2], L[:, 3]
    Cx = (X1 + X2) / 2
    Cy = (Y1 + Y2) / 2
    angle_rad = np.deg2rad(degrees)
    cos_angle = np.cos(angle_rad)
    sin_angle = np.sin(angle_rad)
    X1r = cos_angle * (X1 - Cx) - sin_angle * (Y1 - Cy) + Cx
    Y1r = sin_angle * (X1 - Cx) + cos_angle * (Y1 - Cy) + Cy
    X2r = cos_angle * (X2 - Cx) - sin_angle * (Y2 - Cy) + Cx
    Y2r = sin_angle * (X2 - Cx) + cos_angle * (Y2 - Cy) + Cy
    L_rotated = np.column_stack((X1r, Y1r, X2r, Y2r))
    return L_rotated


def new_remove_segmented_that_are_selected_twice(
    sub_1: np.ndarray,
    idx_1: np.ndarray,
    coh_1: Optional[np.ndarray],
    sub_2: np.ndarray,
    idx_2: np.ndarray,
    coh_2: Optional[np.ndarray],
) -> Tuple[np.ndarray, Optional[np.ndarray], np.ndarray, Optional[np.ndarray]]:
    """
    Removes segments that are selected in both subsets.

    Args:
        sub_1: First subset of lines.
        idx_1: Indices of the first subset in the original array.
        coh_1: Coherence values for the first subset.
        sub_2: Second subset of lines.
        idx_2: Indices of the second subset in the original array.
        coh_2: Coherence values for the second subset.

    Returns:
        sub_1_c: Filtered first subset without duplicates.
        coh_1_c: Coherence values for the filtered first subset.
        sub_2_c: Filtered second subset without duplicates.
        coh_2_c: Coherence values for the filtered second subset.
    """
    idx_1_set = set(idx_1.tolist())
    idx_2_set = set(idx_2.tolist())
    common_indices = idx_1_set & idx_2_set

    idx_1_rm = [i for i, idx in enumerate(idx_1) if idx in common_indices]
    idx_2_rm = [i for i, idx in enumerate(idx_2) if idx in common_indices]

    sub_1_c = np.delete(sub_1, idx_1_rm, axis=0)
    coh_1_c = np.delete(coh_1, idx_1_rm) if coh_1 is not None else None

    sub_2_c = np.delete(sub_2, idx_2_rm, axis=0)
    coh_2_c = np.delete(coh_2, idx_2_rm) if coh_2 is not None else None

    return sub_1_c, coh_1_c, sub_2_c, coh_2_c


def pclines_local_orientation_filtering(
    img_in: np.ndarray,
    m_lsd: np.ndarray,
    coherence: Optional[np.ndarray] = None,
    output_folder: Optional[str] = None,
    outlier_th: float = 0.03,
    debug: bool = True,
) -> Tuple[np.ndarray, Optional[np.ndarray], bool]:
    """
    Filters lines based on local orientation using TS-space transformations.

    Args:
        img_in: Input image array.
        m_lsd: Array of line segments.
        coherence: Optional array of coherence values.
        output_folder: Directory to save debug outputs.
        outlier_th: Residual threshold for inliers.
        debug: Whether to save debug outputs.

    Returns:
        m_lsd_intersecting: Filtered array of line segments after local orientation filtering.
        coherence_intersecting: Coherence values for the filtered line segments.
        radial_alineation: Whether the radial alignment is considered good.
    """
    m_lsd_radial, idx_lsd_radial, coherence_radial, _ = get_converging_lines_pc(
        img_in,
        m_lsd,
        coherence,
        (
            str(Path(output_folder) / "lsd_converging_lines")
            if output_folder is not None
            else None
        ),
        outlier_th=outlier_th,
        debug=debug,
    )

    l_rotated_lsd_lines = rotate_lines(m_lsd)
    sub_2, idx_2, coherence_2, radial_alineation = get_converging_lines_pc(
        img_in,
        l_rotated_lsd_lines,
        coherence,
        (
            str(Path(output_folder) / "lsd_rotated_converging_lines")
            if output_folder is not None
            else None
        ),
        outlier_th=outlier_th,
        debug=debug,
    )

    m_lsd_radial, coherence_radial, sub_2, coherence_2 = (
        new_remove_segmented_that_are_selected_twice(
            m_lsd_radial, idx_lsd_radial, coherence_radial, sub_2, idx_2, coherence_2
        )
    )

    converging_lines = np.vstack((m_lsd_radial, sub_2))
    converging_coherence = (
        np.hstack((coherence_radial, coherence_2)) if coherence is not None else None
    )
    m_lsd_intersecting, _, coherence_intersecting, _ = get_converging_lines_pc(
        img_in,
        converging_lines,
        converging_coherence,
        (
            str(Path(output_folder) / "both_subset_convering_lines")
            if output_folder is not None
            else None
        ),
        outlier_th=outlier_th,
        debug=debug,
    )

    return m_lsd_intersecting, coherence_intersecting, True
