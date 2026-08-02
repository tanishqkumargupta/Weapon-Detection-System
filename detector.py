import pathlib
import sys
import torch
import cv2

ROOT = pathlib.Path(__file__).parent.resolve()
YOLO_PATH = ROOT / "yolov5"

if str(YOLO_PATH) not in sys.path:
    sys.path.insert(0, str(YOLO_PATH))

model = torch.hub.load(
    str(YOLO_PATH),
    "custom",
    path=str(ROOT / "weights" / "best.pt"),
    source="local"
)

model.conf = 0.45


def detect(frame):
    """
    Runs YOLO detection on a frame.

    Returns:
        rendered_frame
        detections
    """

    results = model(frame)

    rendered = results.render()[0]

    detections = []

    for *box, conf, cls in results.xyxy[0].tolist():

        detections.append({
            "class": model.names[int(cls)],
            "confidence": float(conf)
        })

    return rendered, detections