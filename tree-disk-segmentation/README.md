# Tree Disk Segmentation

## Installation
```bash
python -m venv venv
source venv/bin/activate # On Windows use: venv\Scripts\activate
pip install -r requirements.txt
```

## Usage Examples

### Basic Usage
```bash
python main.py --input path/to/input_image.jpg --output path/to/output_image.jpg
```

Example:
```bash
python main.py --input ./input/baumscheibe.jpg --output ./output/output.jpg
```

### Specifying the Model Path
```bash
python main.py --input ./input/baumscheibe.jpg --output ./output/output.jpg --model ./models/segmentation/u2net.pth
```

## Command-Line Arguments
* `--input` (str, required): Path to the input image.
* `--output` (str, required): Path to save the output image.
* `--model` (str, optional): Path to the pre-trained model weights. Default is ./models/segmentation/u2net.pth.
