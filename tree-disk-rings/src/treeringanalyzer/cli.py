import argparse
from .main import run_tree_ring_detection


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Tree Ring Detection CLI")
    parser.add_argument("--input", required=True, help="Path to input image")
    parser.add_argument("--cx", type=int, required=True, help="Pith x-coordinate")
    parser.add_argument("--cy", type=int, required=True, help="Pith y-coordinate")
    parser.add_argument("--output_dir", required=True, help="Output directory")
    parser.add_argument(
        "--root_dir", default="./", help="Root directory of the repository"
    )
    parser.add_argument(
        "--sigma", type=float, default=3.0, help="Edge detector Gaussian kernel"
    )
    parser.add_argument(
        "--th_low", type=float, default=5.0, help="Low threshold for gradient"
    )
    parser.add_argument(
        "--th_high", type=float, default=20.0, help="High threshold for gradient"
    )
    parser.add_argument(
        "--height", type=int, default=0, help="Resize height (0 to keep original)"
    )
    parser.add_argument(
        "--width", type=int, default=0, help="Resize width (0 to keep original)"
    )
    parser.add_argument(
        "--alpha", type=float, default=30.0, help="Collinearity threshold"
    )
    parser.add_argument("--nr", type=int, default=360, help="Number of rays")
    parser.add_argument(
        "--min_chain_length", type=int, default=2, help="Minimum chain length"
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument(
        "--save_imgs", action="store_true", help="Save intermediate images"
    )
    return parser.parse_args()


def main():
    args = parse_arguments()

    run_tree_ring_detection(
        input_image_path=args.input,
        output_dir=args.output_dir,
        cx=args.cx,
        cy=args.cy,
        sigma=args.sigma,
        th_low=args.th_low,
        th_high=args.th_high,
        height=args.height,
        width=args.width,
        alpha=args.alpha,
        nr=args.nr,
        mc=args.min_chain_length,
        debug=args.debug,
        save_imgs=args.save_imgs,
        root_dir=args.root_dir,
    )


if __name__ == "__main__":
    main()
