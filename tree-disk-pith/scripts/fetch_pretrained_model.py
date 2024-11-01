import urllib.request, os
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

URLS = {
    "https://github.com/hmarichal93/apd/releases/download/v1.0_icpr_2024_submission/all_best_yolov8.pt": "models/all_best_yolov8.pt",
}

for url, destination in URLS.items():
    logger.info(f"Downloading {url} ...")
    with urllib.request.urlopen(url) as f:
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        open(destination, "wb").write(f.read())
