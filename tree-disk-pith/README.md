# Tree Disk Pith Detection

[![PyPI - Version](https://img.shields.io/pypi/v/tree-disk-pith)](https://pypi.org/project/tree-disk-pith/)

A Python package for analyzing tree rings in cross-sectional images. Originally forked from [hmarichal93/apd](https://github.com/hmarichal93/apd).

## Installation

```bash
pip install tree-disk-pith
```

## Usage

### Python API

```python
import treediskpith

# Configure the analyzer
treediskpith.configure(
    input_image="input/tree-disk4.png",
    model_path="models/apd_dl.h5",
    save_results=True,
)

# Run the detection
(
    img_in,          # Original input image
    img_pre,         # Preprocessed image
    pith,  # Center of the tree disk
) = treediskpith.run()
```

### Command Line Interface (CLI)

Basic usage:
```bash
tree-disk-pith --input_image ./input/tree-disk3.png --model_path ./models/all_best_yolov8.pt
```

Advanced usage with custom parameters:
```bash
tree-disk-pith \
    --input_image input/tree-disk3.png \
    --model_path ./models/all_best_yolov8.pt \
    --output_dir custom_output/ \
    --new_shape 640 \
    --save_results \
    --debug
```

## CLI Arguments

| Argument | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `--input_image` | str | Yes | - | Input image file path |
| `--output_dir` | str | Yes | ./output | Output directory path |
| `--model_path` | str | No | - | Path to the weights file (required if using apd_dl method) |
| `--new_shape` | int | No | 0 | New shape for resizing the input image. If 0, no resizing is done |
| `--debug` | flag | No | False | Enable debug mode to save intermediate images and outputs |
| `--save_results` | flag | No | False | Save intermediate images, labelme and config file |

## Development

### Setting up Development Environment

1. Create and activate virtual environment:
```bash
poetry config virtualenvs.in-project true
poetry env use python
```

```bash
poetry install
eval $(poetry env activate)
```

2. Running tests:
```bash
pytest
```

3. fetch dataset
```bash
python fetch_dataset.py
```

4. Download pretrained model
```bash
python fetch_pretrained_model.py
```
