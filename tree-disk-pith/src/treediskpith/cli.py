import argparse
import logging

from .config import Config
from . import configure, run

logger = logging.getLogger(__name__)


def parse_arguments():
    parser = argparse.ArgumentParser(description="Pith detector")
    parser.add_argument(
        "--input_image", type=str, required=True, help="Input image file path"
    )

    # Method parameters
    parser.add_argument(
        "--output_dir", type=str, default=Config.output_dir, help="Output directory"
    )
    parser.add_argument(
        "--method",
        type=str,
        choices=["apd", "apd_pcl", "apd_dl"],
        default=Config.method,
        help="Method to use: 'apd', 'apd_pcl', or 'apd_dl'",
    )
    parser.add_argument(
        "--model_path",
        type=str,
        default=Config.model_path,
        help="Path to the weights file (required for method 'apd_dl')",
    )
    parser.add_argument(
        "--percent_lo",
        type=float,
        default=Config.percent_lo,
        help="percent_lo parameter",
    )
    parser.add_argument("--st_w", type=int, default=Config.st_w, help="st_w parameter")
    parser.add_argument("--lo_w", type=int, default=Config.lo_w, help="lo_w parameter")
    parser.add_argument(
        "--st_sigma", type=float, default=Config.st_sigma, help="st_sigma parameter"
    )
    parser.add_argument(
        "--new_shape",
        type=int,
        default=Config.new_shape,
        help="New shape for resizing image",
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument(
        "--save_results", action="store_true", help="Save detection results"
    )

    return parser.parse_args()


def main():
    """Main CLI entry point."""
    args = parse_arguments()

    configure(
        input_image=args.input_image,
        output_dir=args.output_dir,
        method=args.method,
        percent_lo=args.percent_lo,
        st_w=args.st_w,
        lo_w=args.lo_w,
        st_sigma=args.st_sigma,
        new_shape=args.new_shape,
        debug=args.debug,
        model_path=args.model_path,
    )

    run()


if __name__ == "__main__":
    main()
