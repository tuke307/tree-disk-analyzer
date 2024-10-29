# Tree Disk Core Detection

forked from [hmarichal93/apd](https://github.com/hmarichal93/apd)

## Installation
```bash
python -m venv venv
source venv/bin/activate # On Windows use: venv\Scripts\activate
pip install -r requirements.txt
```

## Dataset

```bash
python fetch_dataset.py
```

## Download pretrained model
```bash
python fetch_pretrained_model.py
```

## Usage Examples
### Using the Default Method (apd)
```bash
python main.py --filename ./input/F02c.png --output_dir output/ --new_shape 640 --debug
```

### Using the apd_pcl Method (with PCLines Postprocessing)
```bash
python main.py --filename ./input/F02b.png --output_dir output/ --new_shape 640 --debug --method apd_pcl
```

### Using the apd_dl Method (Deep Learning-Based)
```bash
python main.py --filename ./input/F02c.png --output_dir output/ --new_shape 640 --debug --method apd_dl --weights_path checkpoints/yolo/all_best_yolov8.pt
```

Note: Replace checkpoints/yolo/all_best_yolov8.pt with the actual path to your weights file if different.

## Command-Line Arguments

* `--filename` (str, required): Input image file path.
* `--output_dir` (str, required): Output directory path.
* `--method` (str, optional): Detection method to use. Choices are apd, apd_pcl, or apd_dl. Default is apd.
* `--weights_path` (str, optional): Path to the weights file (required if using apd_dl method).
* `--percent_lo` (float, optional): percent_lo parameter for the algorithm. Default is 0.7.
* `--st_w` (int, optional): st_w parameter for the algorithm. Default is 3.
* `--lo_w` (int, optional): lo_w parameter for the algorithm. Default is 3.
* `--st_sigma` (float, optional): st_sigma parameter for the algorithm. Default is 1.2.
* `--new_shape` (int, optional): New shape for resizing the input image. If 0, no resizing is done. Default is 0.
* `--debug` (flag, optional): Enable debug mode to save intermediate images and outputs.
