"""Project 3: detect common objects in the supplied construction-site image with YOLO."""

from collections import Counter
from pathlib import Path

import cv2
from ultralytics import YOLO


PROJECT_DIR = Path(__file__).resolve().parent
IMAGE_FILE = PROJECT_DIR / "data" / "construction.png"
OUTPUT_DIR = PROJECT_DIR / "outputs"
MODEL_NAME = "yolo11n.pt"


def main() -> None:
    if not IMAGE_FILE.exists():
        raise FileNotFoundError(f"Input image not found: {IMAGE_FILE}")

    OUTPUT_DIR.mkdir(exist_ok=True)
    model = YOLO(MODEL_NAME)
    result = model(IMAGE_FILE, verbose=False)[0]

    class_ids = result.boxes.cls.int().tolist() if result.boxes is not None else []
    counts = Counter(result.names[class_id] for class_id in class_ids)
    annotated_image = result.plot()
    output_image = OUTPUT_DIR / "construction_detected.jpg"
    cv2.imwrite(str(output_image), annotated_image)

    summary_lines = ["Construction-image detection summary", "=" * 36]
    if counts:
        summary_lines.extend(f"{label}: {count}" for label, count in sorted(counts.items()))
    else:
        summary_lines.append("No objects were detected.")
    summary_lines.extend([
        "",
        "Human review is required. A general pretrained model may miss or misclassify construction-specific safety equipment.",
    ])
    summary_file = OUTPUT_DIR / "detection_summary.txt"
    summary_file.write_text("\n".join(summary_lines) + "\n", encoding="utf-8")
    print("\n".join(summary_lines))
    print(f"\nSaved annotated image: {output_image}")
    print(f"Saved summary: {summary_file}")


if __name__ == "__main__":
    main()
