import pytest
from pathlib import Path
import treediskpithdetector as tdc

# set root folder
root_folder = Path(__file__).parent.parent.absolute()


def test_treediskpithdetector_apd():
    filename = root_folder / "input" / "tree-disk1.jpg"
    output_dir = root_folder / "output" / "apd"

    # Configure the detector
    tdc.configure(
        method="apd",
        filename=filename,
        output_dir=output_dir,
        debug=True,
        save_results=True,
    )

    # Run the detector
    result = tdc.run()

    # Add assertions to verify the expected behavior
    assert result is not None, "The result should not be None"


def test_treediskpithdetector_apd_pcl():
    filename = root_folder / "input" / "tree-disk1.jpg"
    output_dir = root_folder / "output" / "apd_pcl"

    # Configure the detector
    tdc.configure(
        method="apd_pcl",
        filename=filename,
        output_dir=output_dir,
        debug=True,
        save_results=True,
    )

    # Run the detector
    result = tdc.run()

    # Add assertions to verify the expected behavior
    assert result is not None, "The result should not be None"


def test_treediskpithdetector_apd_dl():
    filename = root_folder / "input" / "tree-disk1.jpg"
    output_dir = root_folder / "output" / "apd_dl"
    weights_path = root_folder / "models" / "all_best_yolov8.pt"

    # Configure the detector
    tdc.configure(
        method="apd_dl",
        filename=filename,
        output_dir=output_dir,
        weights_path=weights_path,
        debug=True,
        save_results=True,
    )

    # Run the detector
    result = tdc.run()

    # Add assertions to verify the expected behavior
    assert result is not None, "The result should not be None"


if __name__ == "__main__":
    pytest.main()
