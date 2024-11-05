import argparse
import logging

from . import configure, run

logger = logging.getLogger(__name__)


def parse_arguments():
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
    parser.add_argument(
        "--save_results", action="store_true", help="Save detection results"
    )

    return parser.parse_args()


def main():
    """Main CLI entry point."""
    args = parse_arguments()

    configure(
        filename=args.filename,
        output_dir=args.output_dir,
        method=args.method,
        percent_lo=args.percent_lo,
        st_w=args.st_w,
        lo_w=args.lo_w,
        st_sigma=args.st_sigma,
        new_shape=args.new_shape,
        debug=args.debug,
        weights_path=args.weights_path,
    )

    run()


if __name__ == "__main__":
    main()
