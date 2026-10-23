
# DISC5105 Week 2 — Assignment A1: Video and Insole Pressure Fusion

In this assignment, you will build a small multimodal data-fusion pipeline using a video frame and plantar-pressure measurements from two insoles. You will align the measurements in time, place pressure readings on a shared spatial grid, combine them with an RGB image, and pass the four-channel input through a simplified pose-estimation network.

## Assignment file

- [Project05_Assignment.ipynb](Project05_Assignment.ipynb) — student notebook with instructions, starter code, and automatic checks.

Place the notebook and this README in the same GitHub folder. The notebook uses `S2.mp4` and `S2.txt`. Its setup cell attempts to download missing data files from the course dataset; if the files are already in the notebook's working directory, it uses those copies. If the download fails, obtain both data files from the instructor and put them beside the notebook before running it.

## Learning objectives

By completing the notebook, you will:

1. Match a video frame to the nearest insole-pressure timestamp.
2. Map 16 sensors per foot onto a mirrored `13 × 13` pressure grid.
3. Form a `(1, 4, 128, 128)` tensor with channels ordered `[R, G, B, pressure]`.
4. Implement a compact, two-resolution HRNet-style model that outputs 17 keypoint heatmaps.
5. Inspect the decoded keypoints and verify the pipeline using the supplied checks.

The network is a teaching model with randomly initialized weights. The assignment assesses data alignment, tensor processing, network structure, and interpretation; its keypoint predictions are **not** expected to be accurate poses.

## Tasks and evidence

| Task | What to complete | What to retain in your output |
| --- | --- | --- |
| 1. Time alignment and pressure map | Match the nearest pressure sample and place both feet on the `13 × 13` grid. | Frame and matched times, timing error, map shape, and full pressure matrix. |
| 2. Four-channel fusion | Normalize and resize the pressure map, then combine it with RGB. | Fused tensor shape, value ranges, sampled `[R, G, B, P]` pixel, and pressure preview. |
| 3. Simplified HRNet | Complete the high- and low-resolution branches, fusion, and heatmap head. | Printed model and shape trace for `stem`, `high`, `down`, `low`, `fuse`, and `head`. |
| 4. Verification and interpretation | Inspect decoded keypoints and the supplied automatic checks. | Complete `17 × 3` keypoint matrix, all PASS/FAIL lines, final automatic score, one limitation, and one concrete improvement. |


## Submission

Submit your completed notebook or a PDF that includes the required code and outputs. Add your name and student ID in the notebook, run every cell in order, and keep the evidence listed above. A suggested filename is `DISC5105_project06_datafusion_A1_<YourName>.ipynb`.


