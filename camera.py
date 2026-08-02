import cv2
import detector

model = detector.model


def generate_frames(source=0):

    cap = cv2.VideoCapture(source)

    if not cap.isOpened():
        raise RuntimeError("Unable to open camera")

    while True:

        success, frame = cap.read()

        if not success:
            break

        results = model(frame)

        frame = results.render()[0]

        _, buffer = cv2.imencode(".jpg", frame)

        yield (
            b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' +
            buffer.tobytes() +
            b'\r\n'
        )

    cap.release()