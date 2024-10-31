import argparse
import time
from enum import Enum
from pathlib import Path
from typing import Optional
import logging
import cv2
import numpy as np
import pandas as pd

from src.image import resize_image_using_pil_lib, Color
from src.pith_detector import apd, apd_pcl, apd_dl
from src.io import clear_dir

logger = logging.getLogger(__name__)


class Method(Enum):
    apd = "apd"
    apd_pcl = "apd_pcl"
    apd_dl = "apd_dl"


def main(
    filename: str,
    output_dir: str,
    method: Method = Method.apd,
    percent_lo: float = 0.7,
    st_w: int = 3,
    lo_w: int = 3,
    st_sigma: float = 1.2,
    new_shape: int = 0,
    debug: bool = False,
    weights_path: Optional[str] = None,
) -> np.ndarray:
    """Main function for pith detection.

    Args:
        filename (str): Input image file path.
        output_dir (str): Output directory path.
        method (Method): Detection method to use.
        percent_lo (float): Percent_lo parameter.
        st_w (int): ST_W parameter.
        lo_w (int): LO_W parameter.
        st_sigma (float): ST_Sigma parameter.
        new_shape (int): New shape for resizing the image.
        debug (bool): Enable debug mode.
        weights_path (Optional[str]): Path to the weights file (required for 'apd_dl' method).

    Returns:
        np.ndarray: Coordinates of the detected pith point.
    """
    start_time = time.time()
    output_dir_path = Path(output_dir)
    output_dir_path.mkdir(exist_ok=True, parents=True)

    # Clear output directory
    clear_dir(output_dir_path)

    # Load image
    img_in = cv2.imread(filename)
    if img_in is None:
        raise FileNotFoundError(f"Image file '{filename}' not found.")

    original_height, original_width = img_in.shape[:2]

    # Resize image if needed
    if new_shape > 0:
        img_in = resize_image_using_pil_lib(
            img_in, height_output=new_shape, width_output=new_shape
        )

    if debug:
        resized_debug_image = resize_image_using_pil_lib(img_in, 640, 640)
        cv2.imwrite(str(output_dir_path / "resized.png"), resized_debug_image)

    # Run detection method
    if method == Method.apd:
        logger.info("Using method: apd")
        peak = apd(
            img_in,
            st_sigma,
            st_w,
            lo_w,
            rf=7,
            percent_lo=percent_lo,
            max_iter=11,
            epsilon=1e-3,
            debug=debug,
            output_dir=output_dir_path,
        )
    elif method == Method.apd_pcl:
        logger.info("Using method: apd_pcl")
        peak = apd_pcl(
            img_in,
            st_sigma,
            st_w,
            lo_w,
            rf=7,
            percent_lo=percent_lo,
            max_iter=11,
            epsilon=1e-3,
            debug=debug,
            output_dir=output_dir_path,
        )
    elif method == Method.apd_dl:
        logger.info("Using method: apd_dl")
        if weights_path is None:
            raise ValueError("weights_path must be provided for method 'apd_dl'")
        peak = apd_dl(img_in, output_dir_path, weights_path)
    else:
        raise ValueError(f"Method '{method}' not recognized.")

    if debug:
        img_debug = img_in.copy()
        height, width = img_debug.shape[:2]
        dot_size = max(height // 200, 1)
        x, y = peak
        cv2.circle(
            img_debug,
            (int(round(x)), int(round(y))),
            dot_size,
            Color.blue,
            -1,
        )
        img_debug_resized = resize_image_using_pil_lib(img_debug, 640, 640)
        cv2.imwrite(str(output_dir_path / "peak.png"), img_debug_resized)

    # Convert peak coordinates to original scale
    new_height, new_width = img_in.shape[:2]
    if new_shape > 0:
        scale_x = original_width / new_width
        scale_y = original_height / new_height
        peak = np.array(peak) * np.array([scale_x, scale_y])

    execution_time = time.time() - start_time

    # Save results
    data = {
        "coarse_x": [peak[0]],
        "coarse_y": [peak[1]],
        "exec_time(s)": [execution_time],
    }
    df = pd.DataFrame(data)
    df.to_csv(str(output_dir_path / "pith.csv"), index=False)

    return peak


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pith detector")
    parser.add_argument(
        "--filename", type=str, required=True, help="Input image file path"
    )
    parser.add_argument(
        "--output_dir", type=str, required=True, help="Output directory"
    )

    # Method parameters
    parser.add_argument(
        "--method",
        type=str,
        choices=["apd", "apd_pcl", "apd_dl"],
        default="apd",
        help="Method to use: 'apd', 'apd_pcl', or 'apd_dl'",
    )
    parser.add_argument(
        "--weights_path",
        type=str,
        default=None,
        help="Path to the weights file (required for method 'apd_dl')",
    )
    parser.add_argument(
        "--percent_lo", type=float, default=0.7, help="percent_lo parameter"
    )
    parser.add_argument("--st_w", type=int, default=3, help="st_w parameter")
    parser.add_argument("--lo_w", type=int, default=3, help="lo_w parameter")
    parser.add_argument(
        "--st_sigma", type=float, default=1.2, help="st_sigma parameter"
    )
    parser.add_argument(
        "--new_shape", type=int, default=0, help="New shape for resizing image"
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")

    args = parser.parse_args()

    method = Method(args.method)

    main(
        filename=args.filename,
        output_dir=args.output_dir,
        method=method,
        percent_lo=args.percent_lo,
        st_w=args.st_w,
        lo_w=args.lo_w,
        st_sigma=args.st_sigma,
        new_shape=args.new_shape,
        debug=args.debug,
        weights_path=args.weights_path,
    )
