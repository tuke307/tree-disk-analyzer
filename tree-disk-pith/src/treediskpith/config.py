from dataclasses import dataclass, field
from pathlib import Path
import json
import logging
from typing import Any, Dict, Optional
from datetime import datetime
from .detection.detection_method import DetectionMethod

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
        method (Method): Detection method to use.
        percent_lo (float): Percent_lo parameter for detection.
        st_w (int): ST_W parameter for spatial filtering.
        lo_w (int): LO_W parameter for local optimization.
        st_sigma (float): ST_Sigma parameter for Gaussian filtering.
        new_shape (int): New shape for resizing the image.
        debug (bool): Enable debug mode for additional logging.
        model_path (Optional[str]): Path to model file (required for 'apd_dl' method).
    """

    # -------------- Input/Output Settings ----------------
    input_image: str = ""
    output_dir: str = "./output/"
    method: DetectionMethod = DetectionMethod.APD
    model_path: Optional[str] = None

    # -------------- Processing Parameters ----------------
    percent_lo: float = 0.1
    st_w: int = 5
    lo_w: int = 3
    st_sigma: float = 1.0
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
        if self.method == DetectionMethod.APD_DL and not self.model_path:
            raise ValueError("model_path is required when using APD_DL method")

    def _validate_and_set_paths(self):
        """Validate and set all path-related fields."""
        # Validate input image
        if self.input_image:
            input_path = Path(self.input_image)
            if not input_path.exists():
                raise ValueError(f"Input image file does not exist: {input_path}")
            if not input_path.is_file():
                raise ValueError(f"Input image path is not a file: {input_path}")
            self.input_image = str(input_path.resolve())

        # Set up output directory
        output_path = Path(self.output_dir)
        try:
            self.output_dir = str(ensure_directory(output_path))
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
            self.model_path = str(model_path.resolve())

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
                if key == "method":
                    new_value = DetectionMethod(new_value)
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
            k: (
                v.value
                if isinstance(v, DetectionMethod)
                else str(v) if isinstance(v, Path) else v
            )
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
        ...     method="apd_dl",
        ...     model_path="model.pth",
        ...     st_w=7
        ... )
    """
    config.update(**kwargs)
