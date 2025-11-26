import os, argparse
from ultralytics import YOLO

def main():
    ap = argparse.ArgumentParser(description="Train YOLO on captcha dataset")
    ap.add_argument("--dataset", default="./dataset", type=str)
    ap.add_argument("--imgsz", type=int, default=400)
    ap.add_argument("--epochs", type=int, default=80)
    ap.add_argument("--batch", type=int, default=64)
    ap.add_argument("--project", default=".")
    ap.add_argument("--name", default="yolo11s_model")
    args = ap.parse_args()

    os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"

    # Load a pretrained YOLO11s model (9.4M params)
    model = YOLO("yolo11s.pt")

    model.train(
        data=os.path.join(args.dataset, "captcha.yaml"),
        imgsz=args.imgsz,
        epochs=args.epochs,
        batch=args.batch,
        workers=12,
        project=args.project,
        name=args.name,
        exist_ok=True,
        device=0,
        cache="disk"
    )

if __name__ == "__main__":
    main()