"""
Copyright (c) 2023 Author(s) Henry Marichal (hmarichal93@gmail.com

This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

import os
import json
from pathlib import Path
import cv2
import shutil


def load_image(image_name: str) -> cv2.typing.MatLike:
    img = cv2.imread(image_name)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return img


def load_config(default=True) -> dict:
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


def clear_dir(dir: Path) -> None:
    """Clears all files and directories in the output directory."""
    for item in dir.iterdir():
        if item.is_file():
            item.unlink()
        elif item.is_dir():
            shutil.rmtree(item)
