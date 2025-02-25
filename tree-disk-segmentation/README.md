# Tree Disk Segmentation

[![PyPI - Version](https://img.shields.io/pypi/v/tree-disk-segmentation)](https://pypi.org/project/tree-disk-segmentation/)

A Python package for analyzing tree rings in cross-sectional images.

## Installation

```bash
pip install tree-disk-segmentation
```

## Usage

### Python API

```python
import treedisksegmentation

# Configure the analyzer
treedisksegmentation.configure(
    input_image="input/tree-disk4.png",
    save_results=True,
)

# Run the segmentation
(
    result_image,   # Image with detected tree disks
    masks,          # List of masks for each detected tree disk
) = treedisksegmentation.run()
```

### Command Line Interface (CLI)

Basic usage:
```bash
tree-disk-segmentation --input_image ./input/baumscheibe.jpg --output_dir ./output
```

Save intermediate results:
```bash
tree-disk-segmentation --input_image ./input/baumscheibe.jpg --output_dir ./output --model_path ./models/yolo11s-seg-tree.pt --save_results
```

## CLI Arguments

| Argument | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `--input_image` | str | Yes | - | Path to input image |
| `--output_dir` | str | No | `./output` | Output directory path |
| `--model_path` | str | No | `./models/yolo11s-seg-tree.pt` | Path to the pre-trained model weights |
| `--debug` | flag | No | False | Enable debug mode |
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
poetry run pytest
```
