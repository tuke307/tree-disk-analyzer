# Tree Disk Pith Detection

[![PyPI - Version](https://img.shields.io/pypi/v/tree-disk-pith-detector)](https://pypi.org/project/tree-disk-pith-detector/)

A Python package for analyzing tree rings in cross-sectional images. Originally forked from [hmarichal93/apd](https://github.com/hmarichal93/apd).

## Installation

```bash
pip install tree-disk-pith-detector
```

## Usage

### Python API

```python
import treediskpithdetector

# Configure the analyzer
treediskpithdetector.configure(
    input_image="input/tree-disk4.png",
    save_results=True,
)

# Run the detection
(
    img_in,          # Original input image
    img_pre,         # Preprocessed image
    pith,  # Center of the tree disk
) = treediskpithdetector.run()
```

### Command Line Interface (CLI)

Basic usage:
```bash
tree-disk-pith-detector --input_image ./input/tree-disk3.png --new_shape 640 --debug
```

Save intermediate results:
```bash
tree-disk-pith-detector --input_image ./input/tree-disk3.png --new_shape 640 --debug --method apd_pcl --save_results
```

Advanced usage with custom parameters:
```bash
tree-disk-pith-detector \
    --input_image input/tree-disk3.png \
    --cx 1204 \
    --cy 1264 \
    --output_dir custom_output/ \
    --sigma 4.0 \
    --th_low 10 \
    --th_high 25 \
    --save_results \
    --debug
```

## CLI Arguments

| Argument | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `--input_image` | str | Yes | - | Input image file path |
| `--output_dir` | str | Yes | - | Output directory path |
| `--method` | str | No | apd | Detection method to use. Choices are apd, apd_pcl, or apd_dl |
| `--model_path` | str | No | - | Path to the weights file (required if using apd_dl method) |
| `--percent_lo` | float | No | 0.7 | percent_lo parameter for the algorithm |
| `--st_w` | int | No | 3 | st_w parameter for the algorithm |
| `--lo_w` | int | No | 3 | lo_w parameter for the algorithm |
| `--st_sigma` | float | No | 1.2 | st_sigma parameter for the algorithm |
| `--new_shape` | int | No | 0 | New shape for resizing the input image. If 0, no resizing is done |
| `--debug` | flag | No | False | Enable debug mode to save intermediate images and outputs |
| `--save_results` | flag | No | False | Save intermediate images, labelme and config file |

## Development

### Setting up Development Environment

1. Clone the repository:
```bash
git clone https://github.com/tuke307/tree-disk-pith-detector.git
cd tree-disk-pith-detector
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install development dependencies:
```bash
pip install -r requirements.txt
```

4. Install the package in editable mode:
```bash
pip install -e .
```

5. fetch dataset
```bash
python fetch_dataset.py
```

6. Download pretrained model
```bash
python fetch_pretrained_model.py
```
