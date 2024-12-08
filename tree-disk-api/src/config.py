from pathlib import Path

# Get root directory (2 levels up from config.py)
ROOT_DIR = Path(__file__).parent.parent

# Output Path
OUTPUT_DIR = ROOT_DIR / "output"

# Input Path
INPUT_DIR = ROOT_DIR / "input"

# Define model paths
YOLO_MODEL_PATH = ROOT_DIR / "models" / "all_best_yolov8.pt"
U2NET_MODEL_PATH = ROOT_DIR / "models" / "u2net.pth"
