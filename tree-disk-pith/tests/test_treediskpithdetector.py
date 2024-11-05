import pytest
import treediskpithdetector as tdc


def test_treediskpithdetector_apd():
    # Configure the detector
    tdc.configure(
        method="apd",
        filename="/Users/tonymeissner/source/tree-disk-core-detector/input/tree-disk1.jpg",
        output_dir="/Users/tonymeissner/source/tree-disk-core-detector/output/apd",
        debug=True,
        save_results=True,
    )

    # Run the detector
    result = tdc.run()

    # Add assertions to verify the expected behavior
    assert result is not None, "The result should not be None"


def test_treediskpithdetector_apd_pcl():
    # Configure the detector
    tdc.configure(
        method="apd_pcl",
        filename="/Users/tonymeissner/source/tree-disk-core-detector/input/tree-disk1.jpg",
        output_dir="/Users/tonymeissner/source/tree-disk-core-detector/output/apd_pcl",
        debug=True,
        save_results=True,
    )

    # Run the detector
    result = tdc.run()

    # Add assertions to verify the expected behavior
    assert result is not None, "The result should not be None"


def test_treediskpithdetector_apd_dl():
    # Configure the detector
    tdc.configure(
        method="apd_dl",
        filename="/Users/tonymeissner/source/tree-disk-core-detector/input/tree-disk1.jpg",
        output_dir="/Users/tonymeissner/source/tree-disk-core-detector/output/apd_dl",
        weights_path="/Users/tonymeissner/source/tree-disk-core-detector/models/all_best_yolov8.pt",
        debug=True,
        save_results=True,
    )

    # Run the detector
    result = tdc.run()

    # Add assertions to verify the expected behavior
    assert result is not None, "The result should not be None"


if __name__ == "__main__":
    pytest.main()
