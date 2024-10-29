import os
import json
from pathlib import Path
import cv2


def load_image(image_name):
    img = cv2.imread(image_name)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return img


def load_config(default=True):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    return (
        load_json(f"{dir_path}/../config/default.json")
        if default
        else load_json(f"{dir_path}/../config/general.json")
    )


def load_json(filepath: str) -> dict:
    """
    Load json utility.
    :param filepath: file to json file
    :return: the loaded json as a dictionary
    """
    with open(str(filepath), "r") as f:
        data = json.load(f)
    return data


def write_json(dict_to_save: dict, filepath: str) -> None:
    """
    Write dictionary to disk
    :param dict_to_save: serializable dictionary to save
    :param filepath: path where to save
    :return: void
    """
    with open(str(filepath), "w") as f:
        json.dump(dict_to_save, f)
