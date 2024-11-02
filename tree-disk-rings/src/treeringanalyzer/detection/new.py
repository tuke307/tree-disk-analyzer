import numpy as np
from scipy.ndimage import gaussian_filter as scipy_gaussian_filter
from scipy.ndimage import sobel
from numba import njit, prange
import matplotlib.pyplot as plt

# Constants
FALSE = 0
TRUE = 1
M_PI = np.pi


def error(msg):
    """
    Raises a RuntimeError with the provided message.
    """
    raise RuntimeError(f"error: {msg}")


# @njit(parallel=True)
def compute_edge_points_numba(modG, Gx, Gy, X, Y):
    """
    Identifies sub-pixel edge points using modified non-maximum suppression and sub-pixel correction.
    This function is accelerated using Numba for performance.
    """
    Ex = np.full(X * Y, -1.0, dtype=np.float64)
    Ey = np.full(X * Y, -1.0, dtype=np.float64)
    nonMax = np.zeros(X * Y, dtype=np.float64)

    epsilon = 1000 * np.finfo(np.float64).eps

    for x in prange(2, X - 2):
        for y in range(2, Y - 2):
            idx = x + y * X
            Dx = 0
            Dy = 0
            mod = modG[idx]
            L = modG[(x - 1) + y * X]
            R = modG[(x + 1) + y * X]
            U = modG[x + (y + 1) * X]
            D = modG[x + (y - 1) * X]
            gx = np.abs(Gx[idx])
            gy = np.abs(Gy[idx])

            # Inline the 'greater' logic
            is_greater_L = (mod > L) and ((mod - L) >= epsilon)
            is_greater_R = (mod > R) and ((mod - R) >= epsilon)
            is_not_greater_R = (R > mod) and ((R - mod) >= epsilon)
            is_greater_D = (mod > D) and ((mod - D) >= epsilon)
            is_greater_U = (mod > U) and ((mod - U) >= epsilon)
            is_not_greater_U = (U > mod) and ((U - mod) >= epsilon)

            # Determine if local maximum
            if is_greater_L and not is_greater_R and gx >= gy:
                Dx = 1
            elif is_greater_D and not is_greater_U and gx <= gy:
                Dy = 1

            if Dx > 0 or Dy > 0:
                a = modG[x - Dx + (y - Dy) * X]
                b = modG[x + y * X]
                c = modG[x + Dx + (y + Dy) * X]
                denominator = a - 2 * b + c
                if denominator != 0:
                    offset = 0.5 * (a - c) / denominator
                else:
                    offset = 0.0
                nonMax[idx] = b
                Ex[idx] = x + offset * Dx
                Ey[idx] = y + offset * Dy

    return Ex, Ey, nonMax


def compute_gradient_scipy(image, X, Y):
    """
    Computes the image gradient (Gx, Gy) and its modulus (modG) using SciPy's Sobel filter.
    """
    Gx = sobel(image, axis=1, mode="reflect").astype(np.float64)
    Gy = sobel(image, axis=0, mode="reflect").astype(np.float64)
    modG = np.hypot(Gx, Gy).astype(np.float64)
    return Gx.flatten(), Gy.flatten(), modG.flatten()


def chain(from_idx, to_idx, Ex, Ey, Gx, Gy, X, Y):
    """
    Computes a chaining score between two pixels, favoring closer points.
    """
    if from_idx < 0 or to_idx < 0 or from_idx >= X * Y or to_idx >= X * Y:
        return 0.0

    if from_idx == to_idx:
        return 0.0
    if Ex[from_idx] < 0.0 or Ey[from_idx] < 0.0 or Ex[to_idx] < 0.0 or Ey[to_idx] < 0.0:
        return 0.0

    dx = Ex[to_idx] - Ex[from_idx]
    dy = Ey[to_idx] - Ey[from_idx]
    s_from = Gy[from_idx] * dx - Gx[from_idx] * dy
    s_to = Gy[to_idx] * dx - Gx[to_idx] * dy
    if s_from * s_to <= 0.0:
        return 0.0

    distance = np.sqrt(dx**2 + dy**2)
    if distance == 0.0:
        return 0.0
    if s_from >= 0.0:
        return 1.0 / distance
    else:
        return -1.0 / distance


def chain_edge_points(Ex, Ey, Gx, Gy, X, Y):
    """
    Chains edge points based on gradient directions and proximity.
    """
    next_chain = np.full(X * Y, -1, dtype=np.int32)
    prev_chain = np.full(X * Y, -1, dtype=np.int32)

    for x in range(2, X - 2):
        for y in range(2, Y - 2):
            idx = x + y * X
            if Ex[idx] >= 0.0 and Ey[idx] >= 0.0:
                from_idx = idx
                fwd_s = 0.0
                bck_s = 0.0
                fwd = -1
                bck = -1

                # Examine neighbors within two pixels
                for i in range(-2, 3):
                    for j in range(-2, 3):
                        to = (x + i) + (y + j) * X
                        s = chain(from_idx, to, Ex, Ey, Gx, Gy, X, Y)
                        if s > fwd_s:
                            fwd_s = s
                            fwd = to
                        if s < bck_s:
                            bck_s = s
                            bck = to

                # Handle forward chaining
                if fwd >= 0 and next_chain[from_idx] != fwd:
                    alt = prev_chain[fwd]
                    current_score = chain(from_idx, fwd, Ex, Ey, Gx, Gy, X, Y)
                    if alt < 0 or chain(alt, fwd, Ex, Ey, Gx, Gy, X, Y) < current_score:
                        if next_chain[from_idx] >= 0:
                            prev_chain[next_chain[from_idx]] = -1
                        next_chain[from_idx] = fwd
                        if alt >= 0:
                            next_chain[alt] = -1
                        prev_chain[fwd] = from_idx

                # Handle backward chaining
                if bck >= 0 and prev_chain[from_idx] != bck:
                    alt = next_chain[bck]
                    current_score = chain(from_idx, bck, Ex, Ey, Gx, Gy, X, Y)
                    if alt < 0 or chain(alt, bck, Ex, Ey, Gx, Gy, X, Y) > current_score:
                        if alt >= 0:
                            prev_chain[alt] = -1
                        next_chain[bck] = from_idx
                        if prev_chain[from_idx] >= 0:
                            next_chain[prev_chain[from_idx]] = -1
                        prev_chain[from_idx] = bck

    return next_chain, prev_chain


def thresholds_with_hysteresis(next_chain, prev_chain, modG, X, Y, th_h, th_l):
    """
    Applies hysteresis thresholding to the chained edge points.
    """
    valid = np.zeros(X * Y, dtype=np.int32)

    for i in range(X * Y):
        if (
            (prev_chain[i] >= 0 or next_chain[i] >= 0)
            and not valid[i]
            and modG[i] >= th_h
        ):
            valid[i] = TRUE
            # Follow forwards
            j = i
            while j >= 0 and next_chain[j] >= 0 and not valid[next_chain[j]]:
                k = next_chain[j]
                if modG[k] < th_l:
                    next_chain[j] = -1
                    prev_chain[k] = -1
                    break
                else:
                    valid[k] = TRUE
                    j = k
            # Follow backwards
            j = i
            while j >= 0 and prev_chain[j] >= 0 and not valid[prev_chain[j]]:
                k = prev_chain[j]
                if modG[k] < th_l:
                    prev_chain[j] = -1
                    next_chain[k] = -1
                    break
                else:
                    valid[k] = TRUE
                    j = k

    # Remove any remaining non-valid chained points
    for i in range(X * Y):
        if (prev_chain[i] >= 0 or next_chain[i] >= 0) and not valid[i]:
            prev_chain[i] = -1
            next_chain[i] = -1


def list_chained_edge_points(next_chain, prev_chain, Ex, Ey, X, Y):
    """
    Creates lists of chained edge points and their curve limits.
    """
    x_list = []
    y_list = []
    curve_limits = [0]
    N = 0
    M = 0

    for i in range(X * Y):
        if prev_chain[i] >= 0 or next_chain[i] >= 0:
            # Start a new chain
            curve_limits.append(N)
            M += 1

            # Find the start of the chain
            k = i
            while prev_chain[k] >= 0 and prev_chain[k] != i:
                k = prev_chain[k]

            # Traverse the chain
            first_point = k
            while True:
                # Add to the list
                x_list.append(Ex[k])
                y_list.append(Ey[k])
                N += 1

                # Save the next link
                n = next_chain[k]

                # Unlink the chain
                next_chain[k] = -1
                prev_chain[k] = -1

                if n < 0:
                    break
                if n == first_point:
                    # Closed chain, add the first point again
                    x_list.append(Ex[n])
                    y_list.append(Ey[n])
                    N += 1
                    break
                k = n

    curve_limits.append(N)
    x = np.array(x_list, dtype=np.float64)
    y = np.array(y_list, dtype=np.float64)
    curve_limits = np.array(curve_limits, dtype=int)
    return x, y, curve_limits, N, M


def devernay(image, sigma, th_h, th_l):
    """
    Optimized function to compute sub-pixel edge points using the Canny/Devernay algorithm.

    Parameters:
        image (2D numpy array): Input grayscale image of shape (Y, X). Must be float32 or float64.
        sigma (float): Standard deviation for Gaussian filtering. If sigma=0, no filtering is applied.
        th_h (float): High threshold for hysteresis.
        th_l (float): Low threshold for hysteresis.

    Returns:
        x (1D numpy array): Sub-pixel x-coordinates of edge points.
        y (1D numpy array): Sub-pixel y-coordinates of edge points.
        curve_limits (1D numpy array): Indices in x and y that delimit each curve.
        N (int): Number of edge points.
        M (int): Number of curves.
        Gx (1D numpy array): Gradient in the x-direction.
        Gy (1D numpy array): Gradient in the y-direction.
    """
    if image.ndim != 2:
        error("devernay: input image must be a 2D array")

    Y, X = image.shape

    # Ensure the image is float64 for precision
    if image.dtype == np.float16:
        image = image.astype(np.float32)  # Convert to float32
    elif image.dtype == np.float32:
        image = image.astype(np.float64)  # Convert to float64 for Numba
    elif image.dtype != np.float64:
        image = image.astype(np.float64)  # Convert to float64 if not already

    # Apply Gaussian filter if sigma > 0
    if sigma > 0.0:
        gauss = scipy_gaussian_filter(image, sigma=sigma)
        Gx, Gy, modG = compute_gradient_scipy(gauss, X, Y)
    else:
        Gx, Gy, modG = compute_gradient_scipy(image, X, Y)

    # Identify sub-pixel edge points
    Ex, Ey, nonMax = compute_edge_points_numba(modG, Gx, Gy, X, Y)

    # Chain edge points
    next_chain, prev_chain = chain_edge_points(Ex, Ey, Gx, Gy, X, Y)

    # Apply hysteresis thresholding
    thresholds_with_hysteresis(next_chain, prev_chain, modG, X, Y, th_h, th_l)

    # List chained edge points
    x, y, curve_limits, N, M = list_chained_edge_points(
        next_chain, prev_chain, Ex, Ey, X, Y
    )

    return x, y, curve_limits, N, M, Gx, Gy
