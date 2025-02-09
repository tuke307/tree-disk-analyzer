from pathlib import Path
import os

# Get root directory (3 levels up from config.py)
ROOT_DIR = Path(__file__).parent.parent.parent

# Output Path
OUTPUT_DIR = ROOT_DIR / "output"

# Input Path
INPUT_DIR = ROOT_DIR / "input"

# Define model paths
MODEL_PATH = ROOT_DIR / "models"
YOLO_MODEL_PATH = MODEL_PATH / "all_best_yolov8.pt"
U2NET_MODEL_PATH = MODEL_PATH / "u2net.pth"

DEBUG = os.environ.get("DEBUG", False)
SAVE_RESULTS = os.environ.get("SAVE_RESULTS", False)
