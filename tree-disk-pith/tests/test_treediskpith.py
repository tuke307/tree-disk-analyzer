import pytest
from pathlib import Path
import treediskpith as tdp

# set root folder
root_folder = Path(__file__).parent.parent.absolute()


def test_treediskpith_apd():
    input_image = root_folder / "input" / "tree-disk1.jpg"
    output_dir = root_folder / "output" / "apd"

    # Configure the detector
    tdp.configure(
        method="apd",
        input_image=input_image,
        output_dir=output_dir,
        debug=True,
        save_results=True,
    )

    # Run the detector
    result = tdp.run()

    # Add assertions to verify the expected behavior
    assert result is not None, "The result should not be None"


def test_treediskpith_apd_pcl():
    input_image = root_folder / "input" / "tree-disk1.jpg"
    output_dir = root_folder / "output" / "apd_pcl"

    # Configure the detector
    tdp.configure(
        method="apd_pcl",
        input_image=input_image,
        output_dir=output_dir,
        debug=True,
        save_results=True,
    )

    # Run the detector
    result = tdp.run()

    # Add assertions to verify the expected behavior
    assert result is not None, "The result should not be None"


def test_treediskpith_apd_dl():
    input_image = root_folder / "input" / "tree-disk1.jpg"
    output_dir = root_folder / "output" / "apd_dl"
    model_path = root_folder / "models" / "all_best_yolov8.pt"

    # Configure the detector
    tdp.configure(
        method="apd_dl",
        input_image=input_image,
        output_dir=output_dir,
        model_path=model_path,
        debug=True,
        save_results=True,
    )

    # Run the detector
    result = tdp.run()

    # Add assertions to verify the expected behavior
    assert result is not None, "The result should not be None"


if __name__ == "__main__":
    pytest.main()
