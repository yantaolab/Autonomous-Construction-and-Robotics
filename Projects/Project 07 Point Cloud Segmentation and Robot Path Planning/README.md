# 3D Semantic Segmentation with PointNet

An introductory Google Colab project for exploring indoor point cloud segmentation with a pretrained PointNet model.

## Overview

Using one room from the S3DIS dataset, you will:

- Run semantic segmentation for 13 indoor classes.
- Compare predictions with ground-truth labels in interactive 3D.
- Evaluate point accuracy, per-class IoU, and room mIoU.
- Explore how block size and stride affect the results.

No model training is required.

## Getting Started

1. Open the project notebook in Google Colab.
2. Select **Runtime → Change runtime type → GPU**.
3. Run the notebook cells in order to prepare the data and load the model.
4. Run **Step 5** for baseline inference.
5. Use **Step 6** to explore the results.
6. Run **Step 7** to experiment with segmentation parameters.

## Interactive Visualization

Step 6 provides four viewing modes:

- **Original RGB:** original point colors.
- **Ground truth:** human-annotated classes.
- **Prediction:** model-predicted classes.
- **Errors:** incorrect predictions in red and correct predictions in gray.

Drag to rotate, scroll to zoom, and hover to inspect labels. Ceiling points are hidden by default for easier viewing.

## Parameter Experiments

In Step 7, modify:

- **BLOCK_SIZE:** the XY side length of each spatial block.
- **STRIDE:** the distance between neighboring block positions.


Smaller strides usually create more overlap and require more computation. Better accuracy is not guaranteed.

## Evaluation

- **Point accuracy:** percentage of evaluated points classified correctly.
- **Per-class IoU:** intersection over union for each class.
- **Room mIoU:** average of valid class IoUs.


These are single-room results, not full-dataset benchmark scores.

Download your results before ending the Colab session. Runtime storage is temporary.

## References

- [PointNet paper](https://arxiv.org/abs/1612.00593)
- [PointNet/PointNet++ PyTorch implementation](https://github.com/yanx27/Pointnet_Pointnet2_pytorch)