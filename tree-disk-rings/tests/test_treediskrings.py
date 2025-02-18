from doctest import debug
import pytest
from pathlib import Path
import treediskrings as tda

# set root folder
root_folder = Path(__file__).parent.parent.absolute()


def test_treediskringss_without_save():
    input_image = root_folder / "input" / "tree-disk4.png"
    output_dir = root_folder / "output"

    # Configure the detector
    tda.configure(
        input_image=input_image,
        output_dir=output_dir,
        cx=1204,
        cy=1264,
        save_results=False,
        debug=True,
    )

    # Run the detector
    (
        avg_ring_count,
        img_out,
    ) = tda.run_age_detect()

    # Add assertions to verify the expected behavior
    assert avg_ring_count is not None, "The result should not be None"
    assert avg_ring_count == 24, "The average ring count should be 24"


def test_treediskrings_with_save():
    input_image = root_folder / "input" / "tree-disk4.png"
    output_dir = root_folder / "output"

    # Configure the detector
    tda.configure(
        input_image=input_image,
        output_dir=output_dir,
        cx=1204,
        cy=1264,
        save_results=True,
        debug=True,
    )

    # Run the detector
    (
        avg_ring_count,
        img_out,
    ) = tda.run_age_detect()

    # Add assertions to verify the expected behavior
    assert avg_ring_count is not None, "The result should not be None"
    assert avg_ring_count == 24, "The average ring count should be 24"


if __name__ == "__main__":
    pytest.main()
