from pathlib import Path
import treedisksegmentation as tds

# set root folder
root_folder = Path(__file__).parent.parent.absolute()


def test_treedisksegmentation():
    input_image = root_folder / "input" / "tree-disk1.jpg"
    output_dir = root_folder / "output"
    model_path = root_folder / "models" / "u2net.pth"

    tds.configure(
        input_image=input_image,
        output_dir=output_dir,
        model_path=model_path,
        debug=True,
        save_results=True,
    )

    result = tds.run()

    assert result is not None, "The result should not be None"


if __name__ == "__main__":
    pytest.main()
