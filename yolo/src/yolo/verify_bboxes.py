from pathlib import Path
from PIL import Image, ImageDraw

# Root dirs
IMG_DIR = Path("dataset/images/train")
LBL_DIR = Path("dataset/labels/train")
OUT_DIR = Path("img_bboxes")


def load_yolo_labels(label_path: Path):
    boxes = []
    with open(label_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) != 5:
                continue  # skip malformed lines
            cls_id, xc, yc, w, h = parts
            boxes.append(
                (
                    int(cls_id),
                    float(xc),
                    float(yc),
                    float(w),
                    float(h),
                )
            )
    return boxes


def draw_boxes(image_path: Path, label_path: Path, out_path: Path):
    img = Image.open(image_path).convert("RGB")
    W, H = img.size
    draw = ImageDraw.Draw(img)

    boxes = load_yolo_labels(label_path)

    for cls_id, xc, yc, w, h in boxes:
        # Convert normalized YOLO coords to pixel coords
        box_w = w * W
        box_h = h * H
        cx = xc * W
        cy = yc * H

        x_min = cx - box_w / 2
        y_min = cy - box_h / 2
        x_max = cx + box_w / 2
        y_max = cy + box_h / 2

        draw.rectangle(
            [(x_min, y_min), (x_max, y_max)],
            outline="red",
            width=2,
        )

        text = str(cls_id)
        tb = draw.textbbox((0, 0), text)
        tw = tb[2] - tb[0]
        th = tb[3] - tb[1]
        text_x = x_min
        text_y = max(0, y_min - th - 2)

        draw.rectangle(
            [(text_x, text_y), (text_x + tw + 4, text_y + th + 2)],
            fill="red",
        )
        draw.text((text_x + 2, text_y + 1), text, fill="white")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path)
    print(f"Saved boxed image to: {out_path}")


def main():
    if not IMG_DIR.exists():
        raise SystemExit(f"Image directory not found: {IMG_DIR}")
    if not LBL_DIR.exists():
        raise SystemExit(f"Label directory not found: {LBL_DIR}")

    exts = {".png", ".jpg", ".jpeg"}

    for img_path in sorted(IMG_DIR.iterdir()):
        if img_path.suffix.lower() not in exts:
            continue

        label_path = LBL_DIR / (img_path.stem + ".txt")
        if not label_path.exists():
            print(f"[WARN] No label for {img_path.name}, skipping")
            continue

        out_path = OUT_DIR / img_path.name
        draw_boxes(img_path, label_path, out_path)


if __name__ == "__main__":
    main()
