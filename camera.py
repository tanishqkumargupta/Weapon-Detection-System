import cv2
import os
from datetime import datetime

from detector import detect
from db_models import db, Detection
from flask import current_app
from email_service import send_alert_email

last_saved = None
last_email = None


def generate_frames(source=0):

    global last_saved, last_email

    cap = cv2.VideoCapture(source)

    if not cap.isOpened():
        raise RuntimeError("Unable to open camera")

    while True:

        success, frame = cap.read()

        if not success:
            break

        rendered, detections = detect(frame)

        threats = [
            d for d in detections
            if d["class"].lower() != "person"
        ]

        if threats:

            now = datetime.now()

            if (
                last_saved is None
                or (now - last_saved).total_seconds() >= 5
            ):

                filename = now.strftime("%Y%m%d_%H%M%S") + ".jpg"

                path = os.path.join(
                    current_app.static_folder,
                    "snapshots",
                    filename
                )

                cv2.imwrite(path, rendered)

                for item in threats:

                    detection = Detection(
                        filename=filename,
                        threat=item["class"],
                        confidence=item["confidence"],
                        source="Live Camera"
                    )

                    db.session.add(detection)

                db.session.commit()

                if (
                    last_email is None
                    or (now - last_email).total_seconds() >= 60
                ):

                    send_alert_email(
                        receiver=os.environ.get("ALERT_EMAIL"),
                        threat=threats[0]["class"],
                        confidence=threats[0]["confidence"],
                        timestamp=now.strftime("%d %b %Y | %I:%M %p"),
                        image_path=path
                    )

                    last_email = now

                last_saved = now

        _, buffer = cv2.imencode(".jpg", rendered)

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n"
            + buffer.tobytes()
            + b"\r\n"
        )

    cap.release()