from ultralytics import YOLO
from multiprocessing import freeze_support

if __name__ == '__main__':
    # Add freeze_support for Windows multiprocessing
    freeze_support()
    
    # Load a smaller model for faster training
    model = YOLO('yolov8n.pt')  # Using nano model for fastest training

    # Train the model with optimized parameters for better tool detection
    results = model.train(
        data='data.yaml',
        epochs=20,  # Slightly increased epochs
        imgsz=320,  # Increased image size for better detection
        batch=16,   # Balanced batch size
        patience=0,  # Disabled early stopping
        save=True,
        device='0',  # Use GPU
        workers=2,  # Reduced workers
        project='runs/detect',
        name='train',
        exist_ok=True,
        pretrained=True,
        optimizer='Adam',  # Using Adam for better convergence
        verbose=True,
        seed=42,
        deterministic=True,
        single_cls=False,
        rect=True,  # Enable rectangular training for speed
        cos_lr=True,  # Enable cosine learning rate
        close_mosaic=0,  # Disabled for speed
        resume=False,
        amp=True,  # Keep mixed precision for speed
        fraction=1.0,
        cache=True,  # Enable caching for speed
        overlap_mask=True,
        mask_ratio=4,
        dropout=0.1,  # Added dropout for better generalization
        val=True,
        plots=True,
        lr0=0.001,  # Lower learning rate for better stability
        lrf=0.01,   # Final learning rate
        momentum=0.937,  # SGD momentum
        weight_decay=0.0005,  # L2 regularization
        warmup_epochs=2,  # Slightly increased warmup
        warmup_momentum=0.8,  # Warmup momentum
        warmup_bias_lr=0.1,  # Warmup bias learning rate
        box=7.5,  # Box loss gain
        cls=1.0,  # Increased class loss gain
        dfl=1.5,  # Distribution focal loss gain
        hsv_h=0.015,  # HSV-Hue augmentation
        hsv_s=0.7,  # HSV-Saturation augmentation
        hsv_v=0.4,  # HSV-Value augmentation
        degrees=0.0,  # Disabled for speed
        translate=0.1,  # Translation augmentation
        scale=0.5,  # Scale augmentation
        shear=0.0,  # Disabled for speed
        perspective=0.0,  # Disabled for speed
        flipud=0.0,  # Disabled for speed
        fliplr=0.5,  # Keep flip left-right augmentation
        mosaic=0.0,  # Disabled for speed
        mixup=0.0,  # Disabled for speed
        copy_paste=0.0  # Disabled for speed
    ) 