import pytest
from pathlib import Path
import treediskanalyzer as tda

# set root folder
root_folder = Path(__file__).parent.parent.absolute()


def test_treediskanalyzer():
    input_image = root_folder / "input" / "tree-disk1.jpg"
    output_dir = root_folder / "output" / "apd"

    # Configure the detector
    tda.configure(
        input_image=input_image,
        output_dir=output_dir,
        cx=538,
        cy=408,
        debug=True,
        save_results=True,
    )

    # Run the detector
    result = tda.run()

    # Add assertions to verify the expected behavior
    assert result is not None, "The result should not be None"


if __name__ == "__main__":
    pytest.main()
