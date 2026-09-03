# Project 03 — Construction Tool Classification

A YOLO-based computer vision project for detecting and recognizing common construction tools from images, videos, and webcam input.

This project is part of the `Autonomous-Construction-and-Robotics` repository and contains a complete workflow for dataset organization, YOLO model training, object detection, and Google Colab-based inference.

## Overview

The project uses Ultralytics YOLO to identify five types of construction tools:

- **Drill**
- **Hammer**
- **Pliers**
- **Screwdriver**
- **Wrench**

The dataset configuration contains separate training, validation, and test image directories. The trained model is stored under `runs/detect/train/weights/best.pt`.

The project provides two main ways to run inference:

1. **Google Colab notebook** — recommended for an easy, step-by-step demonstration.
2. **`detect.py`** — command-line inference for images, videos, and webcam input.

## Project Structure

```text
Project 03 Construction Tool Classification/
│
├── images/
├── train/
│   └── images/
├── valid/
│   └── images/
├── test/
│   └── images/
│
├── runs/
│   └── detect/
│       └── train/
│           └── weights/
│               └── best.pt
│
├── data.yaml
├── train.py
├── detect.py
├── YOLO_Detection_Colab.ipynb
├── A3_Assignment_Question.docx
├── A3_Construction_Tool_Classification_Tutorial.pptx
└── README.md
```

## Dataset Configuration

The dataset is defined in `data.yaml`.

```yaml
train: ../train/images
val: ../valid/images
test: ../test/images

nc: 5
names: ['Drill', 'Hammer', 'Pliers', 'Screwdriver', 'Wrench']
```

The dataset therefore contains **5 object classes** and uses:

- `train/images` for training
- `valid/images` for validation
- `test/images` for testing

The dataset metadata identifies the source as a Roboflow dataset and specifies a **CC BY 4.0** license.

## Installation

The easiest way to run the demonstration is with Google Colab.

Install Ultralytics:

```bash
pip install -U ultralytics
```

For local execution, make sure Python and the required packages are installed in your environment. The main project scripts use:

- `ultralytics`
- `opencv-python`
- Python standard-library modules such as `argparse`, `pathlib`, `os`, and `sys`

## Google Colab Notebook

`YOLO_Detection_Colab.ipynb` provides a simplified inference workflow for Google Colab.

The notebook performs the following steps:

1. Install Ultralytics.
2. Import the required Python libraries.
3. Configure the GitHub project and file locations.
4. Download the pretrained `best.pt` model.
5. Download a test image from `test/images`.
6. Load the YOLO model.
7. Run object detection.
8. Save the annotated image.
9. Display the detection result in Colab.
10. Print detected classes and confidence scores.

### Running the Notebook

Open:

```text
YOLO_Detection_Colab.ipynb
```

Then execute the cells from top to bottom.

The notebook automatically downloads:

```text
runs/detect/train/weights/best.pt
```

and a selected image from:

```text
test/images/
```

The files are stored temporarily in the Google Colab runtime.

The default local working directory is:

```text
/content/construction_tool_classification/
```

Detection results are saved to:

```text
/content/construction_tool_classification/detection_results/
```

## Changing the Test Image

The notebook uses an `IMAGE_URL` variable to specify the test image.

To test another image, change only the `IMAGE_URL` value in the configuration cell.

For example, select another image from:

```text
test/images/
```

The notebook automatically determines the input filename and creates the corresponding output filename.

## Confidence Threshold

The notebook uses a configurable YOLO confidence threshold:

```python
CONF_THRESHOLD = 0.25
```

For the assignment workflow, the confidence threshold can be changed to:

```text
0.25
0.50
0.75
```

This allows you to compare how the detection results change as the confidence requirement becomes stricter.

In general:

- **0.25** — more detections, including lower-confidence predictions
- **0.50** — more conservative detections
- **0.75** — only high-confidence predictions are retained

When comparing results, pay attention to both missed detections and incorrect detections.

## Model Training

The training script is provided in `train.py`.

The project trains a lightweight YOLOv8 Nano model:

```python
model = YOLO('yolov8n.pt')
```

The main training configuration includes:

- **Model:** YOLOv8 Nano
- **Epochs:** 20
- **Image size:** 320
- **Batch size:** 16
- **Optimizer:** Adam
- **Initial learning rate:** 0.001
- **GPU:** device `0`
- **Seed:** 42
- **Mixed precision:** enabled
- **Rectangular training:** enabled
- **Cosine learning rate:** enabled

Training results are written to:

```text
runs/detect/train/
```

The trained weights used for inference are:

```text
runs/detect/train/weights/best.pt
```

## Detection with `detect.py`

The command-line detector supports:

- image detection
- video detection
- webcam detection
- configurable confidence thresholds
- configurable model weights
- configurable output directories

### Detect an Image

```bash
python detect.py \
    --source test/images/<image-file>.jpg \
    --weights runs/detect/train/weights/best.pt \
    --conf 0.25 \
    --output runs/detect/predict
```

The annotated image is saved in the specified output directory.

### Detect a Video

```bash
python detect.py \
    --source <video-file>.mp4 \
    --weights runs/detect/train/weights/best.pt \
    --conf 0.25 \
    --output runs/detect/predict
```

The annotated video is saved with an `_annotated.mp4` suffix.

### Webcam Detection

```bash
python detect.py \
    --source webcam \
    --weights runs/detect/train/weights/best.pt \
    --conf 0.25
```

The webcam detector uses camera index `0` by default.

To use another camera:

```bash
python detect.py \
    --source webcam \
    --cam 1 \
    --weights runs/detect/train/weights/best.pt \
    --conf 0.25
```

To save the webcam result as a video:

```bash
python detect.py \
    --source webcam \
    --weights runs/detect/train/weights/best.pt \
    --conf 0.25 \
    --output runs/detect/predict \
    --save-webcam
```

Press `q` to stop webcam detection.

## Command-Line Arguments

`detect.py` provides the following main arguments:

| Argument | Default | Description |
|---|---|---|
| `--source` | `webcam` | Webcam or path to an image/video |
| `--conf` | `0.05` | Detection confidence threshold |
| `--weights` | `runs/detect/train/weights/best.pt` | Model weights |
| `--output` | `runs/detect/predict` | Output directory |
| `--cam` | `0` | Webcam index |
| `--save-webcam` | disabled | Save webcam output to a video |

The default confidence value in `detect.py` is `0.05`, while the Google Colab assignment notebook sets `CONF_THRESHOLD = 0.25` and is intended to compare `0.25`, `0.50`, and `0.75`.

## Detection Output

For image inference, the YOLO result is rendered using:

```python
results[0].plot()
```

The resulting annotated image contains the detected object bounding boxes, class labels, and confidence scores.

The Colab notebook additionally prints detections in the form:

```text
<class name>: <confidence>
```

For example:

```text
Hammer: 0.913
Wrench: 0.846
```

The exact output depends on the input image and confidence threshold.

## Recommended Workflow

For the assignment/demo workflow, the recommended sequence is:

```text
1. Open YOLO_Detection_Colab.ipynb
        ↓
2. Install Ultralytics
        ↓
3. Download best.pt
        ↓
4. Select an image from test/images
        ↓
5. Set CONF_THRESHOLD = 0.25
        ↓
6. Run detection and inspect the result
        ↓
7. Repeat with CONF_THRESHOLD = 0.50
        ↓
8. Repeat with CONF_THRESHOLD = 0.75
        ↓
9. Compare the three results
```

Images containing multiple tools are particularly useful when evaluating detection performance because they allow several object predictions to be examined in a single image.

## Files in This Project

### `data.yaml`

Defines the dataset paths, number of classes, class names, and dataset metadata.

### `train.py`

Trains the YOLO model using the configured dataset and training parameters.

### `detect.py`

Provides command-line inference for images, videos, and webcam streams.

### `YOLO_Detection_Colab.ipynb`

Provides a beginner-friendly Google Colab workflow for downloading the trained model, running inference on test images, saving results, and inspecting detected classes and confidence scores.

### `runs/detect/train/weights/best.pt`

The trained YOLO model weights used by the inference workflow.

### `train/`, `valid/`, and `test/`

Contain the dataset images used for training, validation, and testing.

## Notes

- The trained model is loaded from `runs/detect/train/weights/best.pt`.
- Test images are located under `test/images`.
- The Google Colab notebook downloads these files from the GitHub project at runtime rather than requiring them to be uploaded manually.
- GitHub's normal repository `/tree/` pages are web pages; direct file downloads in the notebook therefore use GitHub's raw-content endpoint.
- The Colab output directory exists only for the current runtime session unless the results are downloaded or copied elsewhere.
- Detection quality depends on the trained model, image content, lighting, object size, viewpoint, and confidence threshold.

## Related Files

- `data.yaml` — dataset configuration
- `train.py` — model training
- `detect.py` — image/video/webcam inference
- `YOLO_Detection_Colab.ipynb` — Google Colab inference tutorial
- `A3_Assignment_Question.docx` — assignment questions
- `A3_Construction_Tool_Classification_Tutorial.pptx` — project tutorial

## Acknowledgement

This project is part of the `Autonomous-Construction-and-Robotics` repository developed for construction automation and robotics applications.

The dataset metadata in `data.yaml` identifies the dataset as:

- Workspace: `drone-fcvjd`
- Project: `tools-bynck`
- Version: `7`
- License: `CC BY 4.0`

Please follow the applicable dataset and repository licensing requirements when reusing the data, model, or project materials.

We would like to thank [Mohit Kattungal](https://github.com/mohitkattungal) and the contributors of the original [toolbox_detection](https://github.com/mohitkattungal/toolbox_detection/tree/main) repository for their work and for making it available as an open-source resource.

