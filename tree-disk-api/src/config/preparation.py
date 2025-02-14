import logging
import gdown
from .settings import (
    INPUT_DIR,
    OUTPUT_DIR,
    MODEL_PATH,
    U2NET_MODEL_PATH,
    YOLO_MODEL_PATH,
)

logger = logging.getLogger(__name__)


def download_u2net_model():
    """
    Download the model from Google Drive.
    """
    file_id = "1ao1ovG1Qtx4b7EoskHXmi2E9rp5CHLcZ"
    url = f"https://drive.google.com/uc?id={file_id}"

    logger.info(f"Downloading Google Drive file from: {url}")

    gdown.download(url, str(U2NET_MODEL_PATH), quiet=False)


def download_yolo_model():
    """
    Download the model from Google Drive.
    """
    file_id = "1_-dDH4DNiL8wbgiPWPaNqne7kbJyZc8z"
    url = f"https://drive.google.com/uc?id={file_id}"

    logger.info(f"Downloading Google Drive file from: {url}")

    gdown.download(url, str(YOLO_MODEL_PATH), quiet=False)


def create_dirs():
    """
    Create necessary directories if they do not exist.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    MODEL_PATH.mkdir(parents=True, exist_ok=True)


create_dirs()
download_u2net_model()
download_yolo_model()
