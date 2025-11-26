from pathlib import Path
from collections import defaultdict

import numpy as np
from ultralytics import YOLO


def infer_repeated_char(weights_path: str, session_dir: str, imgsz: int = 400, conf_th: float = 0.6, device: str | int = 0):
    model = YOLO(weights_path)

    # Collect all images in this session folder
    session_dir = Path(session_dir)
    image_paths = sorted(
        list(session_dir.glob("*.png"))
        + list(session_dir.glob("*.jpg"))
        + list(session_dir.glob("*.jpeg"))
    )
    if not image_paths:
        raise RuntimeError(f"No images found in {session_dir}")

    # Stats per class id
    total_dets = defaultdict(int) # total number of detections across all images
    images_with_any = defaultdict(set) # images where class appears at least once
    images_with_two_plus = defaultdict(set) # images where class appears at least twice

    for img_path in image_paths:
        # One-image inference
        result = model.predict(
            source=str(img_path),
            imgsz=imgsz,
            conf=conf_th,
            iou=0.5,
            device=device,
            verbose=False,
        )[0]

        boxes = result.boxes
        if boxes is None or len(boxes) == 0:
            continue

        classes = boxes.cls.cpu().numpy().astype(int)

        # Count detections per class in this image
        unique, counts = np.unique(classes, return_counts=True)
        for c, k in zip(unique, counts):
            total_dets[c] += int(k)
            if k >= 1:
                images_with_any[c].add(img_path)
            if k >= 2:
                images_with_two_plus[c].add(img_path)


    if not total_dets:
        # No detections at all
        return None, {}

    # Compute per-class stats
    stats = {}
    for c in total_dets.keys():
        stats[c] = {
            "class_id": c,
            "name": model.names.get(c, str(c)),
            "total_dets": total_dets[c],
            "images_with_any": len(images_with_any[c]),
            "images_with_two_plus": len(images_with_two_plus[c]),
        }

    # Classes that have at least one image with 2 or more detections
    candidates = [c for c, s in stats.items() if s["images_with_two_plus"] > 0]

    if candidates:
        # Choose class with:
        # 1) most images where it appears twice,
        # 2) then most images overall,
        # 3) then most total detections
        def candidate_key(c):
            s = stats[c]
            return (
                s["images_with_two_plus"],
                s["images_with_any"],
                s["total_dets"],
            )

        answer_class = max(candidates, key=candidate_key)
    else:
        # Fallback if no class ever had 2 detections in one image
        # choose the one appearing in the most images / detections
        def fallback_key(c):
            s = stats[c]
            return (
                s["images_with_any"],
                s["total_dets"],
            )

        answer_class = max(stats.keys(), key=fallback_key)

    answer_char = model.names[answer_class]
    return answer_char, stats
