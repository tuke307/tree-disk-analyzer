from dataclasses import dataclass, field
from pathlib import Path
import json
import logging
from typing import Any, Dict, Optional
from datetime import datetime

from .utils.file_utils import ensure_directory

logger = logging.getLogger(__name__)


@dataclass
class Config:
    """Global configuration settings for tree ring detection.

    Tracks changes to settings and provides validation for paths.
    All changes to settings are automatically logged.

    Attributes:
        input_image (str): Input image file path.
        output_dir (str): Output directory path.
        new_shape (int): New shape for resizing the image.
        debug (bool): Enable debug mode for additional logging.
        model_path (Optional[str]): Path to model file.
    """

    # -------------- Input/Output Settings ----------------
    input_image: Optional[Path] = None
    output_dir: Path = Path("./output/")
    model_path: Optional[Path] = None

    # -------------- Processing Parameters ----------------
    new_shape: int = 0

    # -------------- Operation Modes ----------------
    debug: bool = False
    save_results: bool = False

    # -------------- Internal State ----------------
    _change_history: Dict[str, list] = field(default_factory=dict, repr=False)

    def __post_init__(self):
        """Initialize paths and change history tracking."""
        self._validate_and_set_paths()
        self._change_history = {}
        for field_name in self.__dataclass_fields__:
            if not field_name.startswith("_"):
                self._change_history[field_name] = []

        # Validate method-specific requirements
        if not self.model_path:
            logger.warning(
                "model_path is not set yet. It is required for proper operation. Please configure it accordingly."
            )

    def _validate_and_set_paths(self):
        """Validate and set all path-related fields."""
        # Validate input image
        if self.input_image:
            input_path = Path(self.input_image)
            if not input_path.exists():
                raise ValueError(f"Input image file does not exist: {input_path}")
            if not input_path.is_file():
                raise ValueError(f"Input image path is not a file: {input_path}")
            self.input_image = input_path.resolve()

        # Set up output directory
        output_path = Path(self.output_dir)
        try:
            self.output_dir = ensure_directory(output_path)
        except PermissionError:
            raise ValueError(
                f"Cannot create output directory (permission denied): {output_path}"
            )
        except Exception as e:
            raise ValueError(f"Error with output directory: {output_path}, {str(e)}")

        # Validate model path if provided
        if self.model_path:
            model_path = Path(self.model_path)
            if not model_path.exists():
                raise ValueError(f"Model file does not exist: {model_path}")
            if not model_path.is_file():
                raise ValueError(f"Model path is not a file: {model_path}")
            self.model_path = model_path.resolve()

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
        path_params = {"input_image", "output_dir", "model_path"}
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

    def get_change_history(self, param: Optional[str] = None) -> Dict:
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
            k: (str(v) if isinstance(v, Path) else v)
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
            if not key.startswith("_"):
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
        ...     model_path="model.pth",
        ... )
    """
    config.update(**kwargs)
