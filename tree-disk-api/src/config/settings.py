from pathlib import Path
import os
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Get root directory (3 levels up from config.py)
ROOT_DIR = Path(__file__).parent.parent.parent

# Output Path
OUTPUT_DIR = ROOT_DIR / "output"

# Input Path
INPUT_DIR = ROOT_DIR / "input"

# Define model paths
MODEL_PATH = ROOT_DIR / "models"
YOLO_PITH_MODEL_PATH = MODEL_PATH / "yolo11s-det-pith.pt"
YOLO_SEG_MODEL_PATH = MODEL_PATH / "yolo11s-seg-tree.pt"

DEBUG = os.environ.get("DEBUG", "false").lower() == "true"
SAVE_RESULTS = os.environ.get("SAVE_RESULTS", "false").lower() == "true"


def log_settings():
    logger.debug("Settings:")
    logger.debug(f"ROOT_DIR: {ROOT_DIR}")
    logger.debug(f"OUTPUT_DIR: {OUTPUT_DIR}")
    logger.debug(f"INPUT_DIR: {INPUT_DIR}")
    logger.debug(f"MODEL_PATH: {MODEL_PATH}")
    logger.debug(f"YOLO_PITH_MODEL_PATH: {YOLO_PITH_MODEL_PATH}")
    logger.debug(f"YOLO_SEG_MODEL_PATH: {YOLO_SEG_MODEL_PATH}")
    logger.debug(f"DEBUG: {DEBUG}")
    logger.debug(f"SAVE_RESULTS: {SAVE_RESULTS}")
