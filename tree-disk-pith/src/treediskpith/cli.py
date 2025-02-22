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
        "--model_path",
        type=str,
        default=Config.model_path,
        help="Path to the weights file",
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
        new_shape=args.new_shape,
        debug=args.debug,
        save_results=args.save_results,
        model_path=args.model_path,
    )

    run()


if __name__ == "__main__":
    main()
