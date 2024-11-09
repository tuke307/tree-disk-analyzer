from dataclasses import dataclass, field
from pathlib import Path
import json
import logging
from typing import Any, Dict
from datetime import datetime

from .utils.file_utils import ensure_directory

logger = logging.getLogger(__name__)


@dataclass
class Config:
    """Global configuration settings for tree ring detection.

    Tracks changes to settings and provides validation for paths.
    All changes to settings are automatically logged.
    """

    # -------------- Input/Output Settings ----------------

    input_image: str = ""
    """Path to the input image file."""

    output_dir: str = "./output/"
    """Directory where results and debug information will be saved."""

    root_dir: str = "./"
    """Root directory of the project."""

    # -------------- Image Processing Parameters ----------------

    cx: int = None
    """Center x-coordinate in the image."""

    cy: int = None
    """Center y-coordinate in the image."""

    sigma: float = 3.0
    """Gaussian kernel parameter for Canny edge detector. Controls edge smoothing."""

    output_height: int = None
    """Target height for image resizing. If 0, maintains original height."""

    output_width: int = None
    """Target width for image resizing. If 0, maintains original width."""

    # -------------- Edge Detection Parameters ----------------

    th_low: float = 5.0
    """Low threshold on gradient magnitude for Canny edge detector. Controls edge sensitivity."""

    th_high: float = 20.0
    """High threshold on gradient magnitude for Canny edge detector. Controls edge continuity."""

    alpha: float = 30.0
    """Edge filtering parameter (collinearity threshold) in degrees."""

    # -------------- Processing Settings ----------------
    nr: int = 360
    """Number of rays for sampling. Higher values give more precise detection."""

    min_chain_length: int = 2
    """Minimum chain length. Chains shorter than this are filtered out."""

    # -------------- Operation Modes ----------------
    debug: bool = False
    """Enable debug mode for additional logging and visualizations."""

    save_results: bool = False
    """Save intermediate images, labelme and config file."""

    clear_output: bool = True
    """Whether to clear output directory before use."""

    _change_history: Dict[str, list] = field(default_factory=dict, repr=False)
    """Change history tracking."""

    def __post_init__(self):
        """Initialize paths and change history tracking."""
        self._validate_and_set_paths()
        self._change_history = {}
        for field_name in self.__dataclass_fields__:
            if not field_name.startswith("_"):
                self._change_history[field_name] = []

    def _validate_and_set_paths(self):
        """Validate and set all path-related fields."""
        # Validate root directory
        root_path = Path(self.root_dir).resolve()
        if not root_path.exists():
            raise ValueError(f"Root directory does not exist: {root_path}")
        self.root_dir = root_path

        # Set up output directory
        output_path = Path(self.output_dir)
        if not output_path.is_absolute():
            output_path = root_path / output_path

        try:
            self.output_dir = ensure_directory(output_path, clear=self.clear_output)
        except PermissionError:
            raise ValueError(
                f"Cannot create/clear output directory (permission denied): {output_path}"
            )
        except Exception as e:
            raise ValueError(f"Error with output directory: {output_path}, {str(e)}")

        # Validate input image if provided
        if self.input_image:
            input_path = Path(self.input_image)
            if not input_path.is_absolute():
                input_path = root_path / input_path

            if not input_path.exists():
                raise ValueError(f"Input image file does not exist: {input_path}")
            if not input_path.is_file():
                raise ValueError(f"Input image path is not a file: {input_path}")

            self.input_image = input_path.resolve()

    def _log_change(self, param: str, old_value: Any, new_value: Any):
        """Log a parameter change with timestamp."""
        timestamp = datetime.now().isoformat()
        change_record = {
            "timestamp": timestamp,
            "old_value": old_value,
            "new_value": new_value,
        }
        self._change_history[param].append(change_record)
        logger.info(f"Config change: {param} changed from {old_value} to {new_value}")

    def update(self, **kwargs):
        """
        Update configuration with new values and log changes.

        Args:
            **kwargs: Configuration parameters to update.

        Raises:
            ValueError: If parameter doesn't exist or paths are invalid.
        """
        path_params = {"input_image", "root_dir", "output_dir"}
        needs_validation = any(param in path_params for param in kwargs)

        for key, new_value in kwargs.items():
            if not hasattr(self, key):
                raise ValueError(f"Unknown configuration parameter: {key}")

            old_value = getattr(self, key)
            if old_value != new_value:
                setattr(self, key, new_value)
                self._log_change(key, old_value, new_value)

        if needs_validation:
            self._validate_and_set_paths()

    def get_change_history(self, param: str = None) -> Dict:
        """
        Get change history for a specific parameter or all parameters.

        Args:
            param: Optional parameter name. If None, returns all change history.

        Returns:
            Dictionary containing change history.
        """
        if param:
            if param not in self._change_history:
                raise ValueError(f"Unknown parameter: {param}")
            return {param: self._change_history[param]}
        return self._change_history

    def to_dict(self) -> dict:
        """Convert configuration to dictionary, excluding internal fields."""
        return {
            k: str(v) if isinstance(v, Path) else v
            for k, v in self.__dict__.items()
            if not k.startswith("_")
        }

    def to_json(self) -> str:
        """Convert configuration to JSON string."""
        return json.dumps(self.to_dict(), indent=4)

    def log_all_configs(self):
        """Log all current configuration values."""
        logger.info("Current configuration values:")
        for key, value in self.__dict__.items():
            if not key.startswith("_"):  # Skip internal attributes
                logger.info(f"{key}: {value}")


# Global configuration instance
config = Config()


def configure(**kwargs):
    """
    Configure global settings for tree ring detection.

    Args:
        **kwargs: Configuration parameters to update.

    Example:
        >>> configure(
        ...     input_image="sample.jpg",
        ...     cx=100,
        ...     cy=100
        ... )
    """
    config.update(**kwargs)
