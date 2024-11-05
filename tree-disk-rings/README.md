# Tree Disk Analyzer

[![PyPI - Version](https://img.shields.io/pypi/v/tree-disk-analyzer)](https://pypi.org/project/tree-disk-analyzer/)

A Python package for analyzing tree rings in cross-sectional images. Originally forked from [hmarichal93/cstrd_ipol](https://github.com/hmarichal93/cstrd_ipol).

## Installation

```bash
pip install tree-disk-analyzer
```

## Usage

### Python API

```python
import treediskanalyzer

# Configure the analyzer
treediskanalyzer.configure(
    input_image="input/tree-disk4.png",
    cx=1204,
    cy=1264,
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
) = treediskanalyzer.run()
```

### Command Line Interface (CLI)

Basic usage:
```bash
tree-disk-analyzer --input_image input/tree-disk4.png --cx 1204 --cy 1264
```

Save intermediate results:
```bash
tree-disk-analyzer --input_image input/tree-disk4.png --cx 1204 --cy 1264 --save_results
```

Advanced usage with custom parameters:
```bash
tree-disk-analyzer \
    --input_image input/F02c.png \
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
| `--input_image` | str | Yes | - | Path to input image |
| `--cx` | int | Yes | - | Pith x-coordinate |
| `--cy` | int | Yes | - | Pith y-coordinate |
| `--output_dir` | str | No | `./output` | Output directory path |
| `--root` | str | No | Current dir | Root directory of the repository |
| `--sigma` | float | No | 3.0 | Gaussian kernel parameter for edge detection |
| `--th_low` | float | No | 5.0 | Low threshold for gradient magnitude |
| `--th_high` | float | No | 20.0 | High threshold for gradient magnitude |
| `--height` | int | No | 0 | Height after resizing (0 to keep original) |
| `--width` | int | No | 0 | Width after resizing (0 to keep original) |
| `--alpha` | float | No | 30.0 | Edge filtering parameter (collinearity threshold) |
| `--nr` | int | No | 360 | Number of rays |
| `--min_chain_length` | int | No | 2 | Minimum chain length |
| `--debug` | flag | No | False | Enable debug mode |
| `--save_results` | flag | No | False | Save intermediate images, labelme and config file |

## Development

### Setting up Development Environment

1. Clone the repository:
```bash
git clone https://github.com/tuke307/tree-disk-analyzer.git
cd tree-disk-analyzer
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

5. Compile the external C code:
```bash
cd ./externas/devernay_1.0 && make clean && make
```
