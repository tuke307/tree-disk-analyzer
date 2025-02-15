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
        debug=False,
    )

    # Run the detector
    (
        img_in,
        img_pre,
        devernay_edges,
        devernay_curves_f,
        devernay_curves_s,
        devernay_curves_c,
        devernay_curves_p,
    ) = tda.run()

    # Add assertions to verify the expected behavior
    assert devernay_curves_p is not None, "The result should not be None"


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
        debug=False,
    )

    # Run the detector
    (
        img_in,
        img_pre,
        devernay_edges,
        devernay_curves_f,
        devernay_curves_s,
        devernay_curves_c,
        devernay_curves_p,
    ) = tda.run()

    # Add assertions to verify the expected behavior
    assert devernay_curves_p is not None, "The result should not be None"


if __name__ == "__main__":
    pytest.main()
