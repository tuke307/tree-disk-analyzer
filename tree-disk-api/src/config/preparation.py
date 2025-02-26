import logging
import gdown
from .settings import (
    INPUT_DIR,
    OUTPUT_DIR,
    MODEL_PATH,
    YOLO_SEG_MODEL_PATH,
    YOLO_PITH_MODEL_PATH,
)

logger = logging.getLogger(__name__)


def download_yolo_seg_model():
    """
    Download the model from Google Drive.
    """
    if YOLO_SEG_MODEL_PATH.exists():
        logger.info(
            f"Yolo model already exists at {YOLO_SEG_MODEL_PATH}, skipping download."
        )
        return

    file_id = "1b9c2X8nBpxGJvs4LduCw-OQb_X2nzNxA"
    url = f"https://drive.google.com/uc?id={file_id}"

    logger.info(f"Downloading Google Drive file from: {url}")

    gdown.download(url, str(YOLO_SEG_MODEL_PATH), quiet=False)


def download_yolo_pith_model():
    """
    Download the model from Google Drive.
    """
    if YOLO_PITH_MODEL_PATH.exists():
        logger.info(
            f"YOLO model already exists at {YOLO_PITH_MODEL_PATH}, skipping download."
        )
        return

    file_id = "1oqR_F__iz8JFG3U2xtfbzdsFmnx3sP0a"
    url = f"https://drive.google.com/uc?id={file_id}"

    logger.info(f"Downloading Google Drive file from: {url}")

    gdown.download(url, str(YOLO_PITH_MODEL_PATH), quiet=False)


def create_dirs():
    """
    Create necessary directories if they do not exist.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    MODEL_PATH.mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    # When running this file directly, create dirs and download models.
    create_dirs()
    download_yolo_seg_model()
    download_yolo_pith_model()
