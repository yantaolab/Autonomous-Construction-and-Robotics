# Project 3 — Construction Image Recognition

This folder implements the workshop's first YOLO exercise. It uses the provided construction-scene image and a lightweight pretrained YOLO model to create an annotated image and a class-count summary.

## Run

```powershell
python -m pip install -r requirements.txt
python detect_construction.py
```

On the first run, Ultralytics may download the `yolo11n.pt` model. Results are written to `outputs/`.

## Important limitation

The pretrained model detects general object classes. It is not a validated construction-safety or PPE detector, so detections must be reviewed by a person. A dedicated hard-hat / safety-vest model needs correctly annotated training images.
