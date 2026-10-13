from ultralytics import YOLO
import cv2
import argparse
import os
import sys
from pathlib import Path

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def is_image_file(path):
    ext = Path(path).suffix.lower()
    return ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']

def is_video_file(path):
    ext = Path(path).suffix.lower()
    return ext in ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.mpeg']

def save_image(annotated_frame, out_path):
    # annotated_frame is expected to be a numpy array (BGR) from results[0].plot()
    ok = cv2.imwrite(out_path, annotated_frame)
    if not ok:
        raise RuntimeError(f"cv2.imwrite failed for {out_path}")

def detect_image_file(model, image_path, output_dir, conf_threshold=0.05):
    """Detect objects in a single image and save annotated image."""
    results = model.predict(image_path, conf=conf_threshold)
    annotated_frame = results[0].plot()
    # Build output path: if output_dir is a directory, keep original filename
    ensure_dir(output_dir)
    out_filename = Path(image_path).name
    out_path = os.path.join(output_dir, out_filename)
    save_image(annotated_frame, out_path)
    print(f"Annotated image saved to {out_path}")

def detect_video_file(model, video_path, output_dir, conf_threshold=0.05, fps_override=None):
    """Detect objects in a video file and save annotated video."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video file {video_path}")

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = fps_override or cap.get(cv2.CAP_PROP_FPS) or 25.0

    ensure_dir(output_dir)
    out_filename = Path(video_path).stem + "_annotated.mp4"
    out_path = os.path.join(output_dir, out_filename)

    # Use mp4v codec for .mp4 output
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(out_path, fourcc, fps, (width, height))

    frame_idx = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        # Ultralytics can accept numpy frames directly
        results = model.predict(frame, conf=conf_threshold)
        annotated = results[0].plot()
        # Ensure annotated has correct shape and dtype
        if annotated is None:
            print(f"Warning: annotated frame is None at index {frame_idx}")
            continue
        writer.write(annotated)
        frame_idx += 1

    cap.release()
    writer.release()
    print(f"Annotated video saved to {out_path}")

def detect_webcam(model, conf_threshold=0.05, cam_index=0, output_dir=None, save_video=False):
    """Detect objects using webcam; optionally save annotated video."""
    cap = cv2.VideoCapture(cam_index)
    if not cap.isOpened():
        print("Error: Could not open webcam")
        return

    writer = None
    out_path = None
    if save_video and output_dir:
        ensure_dir(output_dir)
        out_path = os.path.join(output_dir, f"webcam_annotated.mp4")
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS) or 20.0
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        writer = cv2.VideoWriter(out_path, fourcc, fps, (width, height))

    print("Starting webcam detection... Press 'q' to quit")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame")
            break

        results = model.predict(frame, conf=conf_threshold)
        annotated_frame = results[0].plot()
        if annotated_frame is None:
            # fallback to original frame if plotting failed
            annotated_frame = frame

        cv2.imshow("YOLOv8 Detection", annotated_frame)

        if writer:
            writer.write(annotated_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    if writer:
        writer.release()
        print(f"Webcam annotated video saved to {out_path}")
    cv2.destroyAllWindows()

def main():
    parser = argparse.ArgumentParser(description='YOLOv8 Object Detection')
    parser.add_argument('--source', type=str, default='webcam',
                        help='Source for detection: "webcam" or path to image/video')
    parser.add_argument('--conf', type=float, default=0.05,
                        help='Confidence threshold (default: 0.05)')
    parser.add_argument('--weights', type=str, default='runs/detect/train/weights/best.pt',
                        help='Path to model weights (default: runs/detect/train/weights/best.pt)')
    parser.add_argument('--output', type=str, default='runs/detect/predict',
                        help='Output directory for annotated results (default: runs/detect/predict)')
    parser.add_argument('--cam', type=int, default=0,
                        help='Webcam index (default: 0)')
    parser.add_argument('--save-webcam', action='store_true',
                        help='If set, save webcam output to a video file in --output')
    args = parser.parse_args()

    # Validate weights file
    if not os.path.exists(args.weights):
        print(f"Error: weights file not found: {args.weights}")
        sys.exit(1)

    # Load the model
    model = YOLO(args.weights)

    source = args.source
    conf = args.conf
    output_dir = args.output

    if source.lower() == 'webcam':
        detect_webcam(model, conf_threshold=conf, cam_index=args.cam, output_dir=output_dir, save_video=args.save_webcam)
        return

    # If source is a file path, check existence
    if not os.path.exists(source):
        print(f"Error: Source file {source} does not exist")
        sys.exit(1)

    # Decide whether image or video
    if is_image_file(source):
        try:
            detect_image_file(model, source, output_dir, conf_threshold=conf)
        except Exception as e:
            print(f"Error while processing image: {e}")
            sys.exit(1)
    elif is_video_file(source):
        try:
            detect_video_file(model, source, output_dir, conf_threshold=conf)
        except Exception as e:
            print(f"Error while processing video: {e}")
            sys.exit(1)
    else:
        # Unknown extension: try treating as image first, then video
        try:
            detect_image_file(model, source, output_dir, conf_threshold=conf)
        except Exception:
            try:
                detect_video_file(model, source, output_dir, conf_threshold=conf)
            except Exception as e:
                print(f"Error: could not process file {source}: {e}")
                sys.exit(1)

if __name__ == "__main__":
    main()
