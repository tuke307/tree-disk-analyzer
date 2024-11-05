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

# Run the analysis
(
    img_in,          # Original input image
    img_pre,         # Preprocessed image
    devernay_edges,  # Detected edges
    devernay_curves_f,  # Filtered curves
    devernay_curves_s,  # Smoothed curves
    devernay_curves_c,  # Connected curves
    devernay_curves_p,  # Final processed curves
) = treedisksegmentation.run()
```

### Command Line Interface (CLI)

Basic usage:
```bash
tree-disk-segmentation --input_image ./input/baumscheibe.jpg --output_dir ./output/output.jpg
```

Save intermediate results:
```bash
tree-disk-segmentation --input_image ./input/baumscheibe.jpg --output_dir ./output/output.jpg --model_path ./models/u2net.pth --save_results
```

## CLI Arguments

| Argument | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `--input_image` | str | Yes | - | Path to input image |
| `--output_dir` | str | No | `./output` | Output directory path |
| `--model_path` | str | No | `./models/u2net.pth` | Path to the pre-trained model weights |
| `--debug` | flag | No | False | Enable debug mode |
| `--save_results` | flag | No | False | Save intermediate images, labelme and config file |

## Development

### Setting up Development Environment

1. Clone the repository:
```bash
git clone https://github.com/tuke307/tree-disk-segmentation.git
cd tree-disk-segmentation
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
