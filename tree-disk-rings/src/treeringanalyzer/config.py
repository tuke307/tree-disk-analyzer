from dataclasses import dataclass
from pathlib import Path
import numpy as np
import json
import logging

from .utils.file_utils import ensure_directory

logger = logging.getLogger(__name__)


@dataclass
class Config:
    """Global configuration settings for tree ring detection."""

    input_image_path: str = ""
    """Path to the input image file."""

    output_dir: str = "./output/"
    """Directory where results and debug information will be saved."""

    root_dir: str = "./"
    """Root directory of the project."""

    devernay_path: str = "externas/devernay_1.0"
    """Path to the Devernay executable, normally in the root directory."""

    cx: int = 0
    """Center x-coordinate in the image."""

    cy: int = 0
    """Center y-coordinate in the image."""

    sigma: float = 3.0
    """Gaussian kernel parameter for Canny edge detector. Controls edge smoothing."""

    th_low: float = 5.0
    """Low threshold on gradient magnitude for Canny edge detector. Controls edge sensitivity."""

    th_high: float = 20.0
    """High threshold on gradient magnitude for Canny edge detector. Controls edge continuity."""

    height: int = 0
    """Target height for image resizing. If 0, maintains original height."""

    width: int = 0
    """Target width for image resizing. If 0, maintains original width."""

    alpha: float = 30.0
    """Edge filtering parameter (collinearity threshold) in degrees."""

    nr: int = 360
    """Number of rays for sampling. Higher values give more precise detection."""

    mc: int = 2
    """Minimum chain length. Chains shorter than this are filtered out."""

    debug: bool = False
    """Enable debug mode for additional logging and visualizations."""

    save_imgs: bool = False
    """Save intermediate images during processing."""

    clear_output: bool = True
    """Whether to clear output directory before use."""

    def __post_init__(self):
        """
        Convert string paths to Path objects, validate paths, and create directories.
        Raises ValueError if paths are invalid.
        """
        # Validate and set root directory
        root_path = Path(self.root_dir).resolve()
        if not root_path.exists():
            raise ValueError(f"Root directory does not exist: {root_path}")
        self.root_dir = root_path

        # Validate and set output directory
        output_path = Path(self.output_dir)
        if not output_path.is_absolute():
            output_path = root_path / output_path

        # Create (and optionally clear) output directory
        try:
            self.output_dir = ensure_directory(output_path, clear=self.clear_output)
        except PermissionError:
            raise ValueError(
                f"Cannot create/clear output directory (permission denied): {output_path}"
            )
        except Exception as e:
            raise ValueError(f"Error with output directory: {output_path}, {str(e)}")

        # Validate input image path
        if self.input_image_path:
            input_path = Path(self.input_image_path)
            if not input_path.is_absolute():
                # Make the path relative to root directory
                input_path = root_path / input_path

            if not input_path.exists():
                raise ValueError(f"Input image file does not exist: {input_path}")
            if not input_path.is_file():
                raise ValueError(f"Input image path is not a file: {input_path}")

            self.input_image_path = input_path.resolve()

        # Validate Devernay path
        if self.devernay_path:
            devernay_path = Path(self.devernay_path)
            if not devernay_path.is_absolute():
                devernay_path = root_path / devernay_path

            if not devernay_path.exists():
                raise ValueError(f"Devernay directory does not exist: {devernay_path}")
            if not devernay_path.is_dir():
                raise ValueError(f"Devernay path is not a directory: {devernay_path}")

            self.devernay_path = devernay_path

    @classmethod
    def from_dict(cls, config_dict: dict) -> "Config":
        """Create a Config instance from a dictionary."""
        return cls(**{k: v for k, v in config_dict.items() if hasattr(cls, k)})

    def update(self, **kwargs):
        """
        Update configuration with new values.
        Re-validates paths when updating path-related parameters.
        """
        path_params = {"input_image_path", "output_dir", "root_dir"}
        needs_validation = any(param in path_params for param in kwargs)

        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise ValueError(f"Unknown configuration parameter: {key}")

        # Re-run post-init if any paths were updated
        if needs_validation:
            self.__post_init__()

    def to_json(self) -> str:
        """Convert the configuration settings to a JSON string."""
        return json.dumps(self.__dict__, default=str, indent=4)

    def to_dict(self) -> dict:
        """Convert the configuration settings to a dictionary."""
        return {
            k: str(v) if isinstance(v, Path) else v for k, v in self.__dict__.items()
        }

    def log_configurations(self):
        """Log all configuration settings."""
        logger.info("Current configuration settings:")

        for key, value in self.__dict__.items():
            logger.info(f"{key}: {value}")


# Global configuration instance
config = Config()


def configure(**kwargs):
    """
    Configure global settings for tree ring detection.

    Args:
        **kwargs: Configuration parameters to update.

    Raises:
        ValueError: If paths don't exist or are invalid.

    Example:
        >>> configure(
        ...     input_image_path="sample.jpg",
        ...     cx=100,
        ...     cy=100,
        ...     sigma=2.5
        ... )
    """
    config.update(**kwargs)
