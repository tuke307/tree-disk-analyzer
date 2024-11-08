import argparse
from .config import Config
from . import run, configure


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Tree Ring Detection CLI",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # Required arguments
    required = parser.add_argument_group("required arguments")
    required.add_argument(
        "--input_image", required=True, help="Path to input image", metavar="PATH"
    )
    required.add_argument(
        "--cx", type=int, required=True, help="Pith x-coordinate", metavar="X"
    )
    required.add_argument(
        "--cy", type=int, required=True, help="Pith y-coordinate", metavar="Y"
    )

    # Optional arguments
    parser.add_argument(
        "--output_dir", default="./output", help="Output directory", metavar="DIR"
    )
    parser.add_argument(
        "--root_dir",
        default="./",
        help="Root directory of the repository",
        metavar="DIR",
    )
    parser.add_argument(
        "--sigma",
        type=float,
        default=Config.sigma,
        help="Edge detector Gaussian kernel parameter",
        metavar="FLOAT",
    )
    parser.add_argument(
        "--th_low",
        type=float,
        default=Config.th_low,
        help="Low threshold for gradient magnitude",
        metavar="FLOAT",
    )
    parser.add_argument(
        "--th_high",
        type=float,
        default=Config.th_high,
        help="High threshold for gradient magnitude",
        metavar="FLOAT",
    )
    parser.add_argument(
        "--height",
        type=int,
        default=Config.output_height,
        help="Resize height (0 to keep original)",
        metavar="INT",
    )
    parser.add_argument(
        "--width",
        type=int,
        default=Config.output_width,
        help="Resize width (0 to keep original)",
        metavar="INT",
    )
    parser.add_argument(
        "--alpha",
        type=float,
        default=Config.alpha,
        help="Collinearity threshold in degrees",
        metavar="FLOAT",
    )
    parser.add_argument(
        "--nr",
        type=int,
        default=Config.nr,
        help="Number of rays for sampling",
        metavar="INT",
    )
    parser.add_argument(
        "--min_chain_length",
        type=int,
        default=Config.min_chain_length,
        help="Minimum chain length for filtering",
        metavar="INT",
    )
    parser.add_argument(
        "--debug", action="store_true", help="Enable debug mode with additional logging"
    )
    parser.add_argument(
        "--save_results",
        action="store_true",
        help="Save intermediate processing images",
    )

    return parser.parse_args()


def main():
    """Main CLI entry point."""
    args = parse_arguments()

    # Configure settings from CLI arguments
    configure(
        input_image=args.input_image,
        root_dir=args.root_dir,
        output_dir=args.output_dir,
        cx=args.cx,
        cy=args.cy,
        sigma=args.sigma,
        th_low=args.th_low,
        th_high=args.th_high,
        output_height=args.height,
        output_width=args.width,
        alpha=args.alpha,
        nr=args.nr,
        min_chain_length=args.min_chain_length,
        debug=args.debug,
        save_results=args.save_results,
    )

    run()


if __name__ == "__main__":
    main()
