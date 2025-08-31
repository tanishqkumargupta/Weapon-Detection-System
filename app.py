import os
import sys
import bcrypt
from datetime import datetime
from yolov5.utils.email_utils import send_security_alert_email

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
YOLOV5_PATH = os.path.join(BASE_DIR, 'yolov5')
sys.path.insert(0, YOLOV5_PATH)

from flask import Flask, render_template, request, redirect, url_for, flash, session, Response
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import cv2
import torch
import numpy as np

from db_models import db, User, SecurityAlert
from yolov5.models.common import DetectMultiBackend
from yolov5.utils.augmentations import letterbox
from yolov5.utils.general import non_max_suppression, scale_coords
from yolov5.utils.torch_utils import select_device

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configure the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:World0Peace%40@localhost/wds'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the db from models.py
db.init_app(app)

# Load YOLOv5 model
device = select_device('')
model = DetectMultiBackend('C:/Users/tkg91/PycharmProjects/Project Exhibition 2/yolov5/runs/train/exp3/weights/best.pt',
                           device=device)

migrate = Migrate(app, db)


# Route for home page
@app.route('/')
def home():
    return render_template('home.html')


# Route for login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):  # Updated this line
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')

    return render_template('login.html')


# Route for signup
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        raw_password = request.form['password']
        confirm_password = request.form['confirmPassword']

        if raw_password != confirm_password:
            flash('Passwords do not match')
            return redirect(url_for('signup'))

        # Hash the password using bcrypt
        hashed_password = bcrypt.hashpw(raw_password.encode('utf-8'), bcrypt.gensalt())
        new_user = User(username=username, email=email, password=hashed_password)

        try:
            db.session.add(new_user)
            db.session.commit()
            flash('User created successfully')
            return redirect(url_for('login'))
        except Exception as e:
            flash(f'Error: {e}')
            db.session.rollback()

    return render_template('signup.html')


# Route for dashboard
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')


# Route to render the live detection page
@app.route('/live-detection')
def live_detection():
    return render_template('live_detection.html')


@app.route('/video-feed')
def video_feed():
    def generate():
        cap = cv2.VideoCapture(0)  # Try adjusting the index if needed
        if not cap.isOpened():
            print("Error: Could not access the camera.")
            return "Error: Could not access the camera"
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Failed to capture image")
                break
            frame = detect_objects(frame)  # Apply YOLO detection
            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                print("Error: Failed to encode frame")
                break
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        cap.release()
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/setup-camera/video-feed')
def setup_camera_feed():
    camera_type = request.args.get('camera_type')
    camera_url = request.args.get('camera_url')

    def generate(source):
        cap = cv2.VideoCapture(source)
        if not cap.isOpened():
            print(f"Error: Could not access the camera at {source}")
            return
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame = detect_objects(frame)
            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                break
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        cap.release()

    if camera_type == 'external' and camera_url:
        return Response(generate(camera_url), mimetype='multipart/x-mixed-replace; boundary=frame')
    else:
        return Response(generate(0), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/detection-history')
def detection_history():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('detection_history.html')


@app.route('/security-alerts')
def security_alerts():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Fetch security alerts for the logged-in user
    user = User.query.get(session['user_id'])
    alerts = SecurityAlert.query.filter_by(user_id=user.id).all()

    return render_template('security_alerts.html', alerts=alerts)


# Function to detect objects
def detect_objects(frame):
    img = letterbox(frame, 640, stride=32, auto=True)[0]
    img = img.transpose((2, 0, 1))[::-1]  # BGR to RGB, to 3xHxW
    img = np.ascontiguousarray(img)

    img_tensor = torch.from_numpy(img).to(device)
    img_tensor = img_tensor.float() / 255.0
    if img_tensor.ndimension() == 3:
        img_tensor = img_tensor.unsqueeze(0)

    pred = model(img_tensor, augment=False, visualize=False)
    pred = non_max_suppression(pred, 0.25, 0.45, classes=None, agnostic=False)

    for det in pred:
        if len(det):
            det[:, :4] = scale_coords(img_tensor.shape[2:], det[:, :4], frame.shape).round()
            for *xyxy, conf, cls in det:
                label = f'{model.names[int(cls)]} {conf:.2f}'
                cv2.rectangle(frame, (int(xyxy[0]), int(xyxy[1])), (int(xyxy[2]), int(xyxy[3])), (0, 255, 0), 2)
                cv2.putText(frame, label, (int(xyxy[0]), int(xyxy[1]) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                            (255, 255, 255), 2)

                # Check if the detected object is a weapon and the confidence is above 67%
                if model.names[int(cls)] in ['weapon', 'gun', 'knife'] and conf >= 0.67:
                    detection_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Get the current time
                    user = User.query.get(session['user_id'])  # Get the current logged-in user from the session
                    if user:
                        send_security_alert_email(user.email, detection_time, conf)  # Send email alert

    return frame


# Route for account settings
@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])

    if request.method == 'POST':
        user.username = request.form['username']
        user.email = request.form['email']

        try:
            db.session.commit()
            flash('Account updated successfully')
        except Exception as e:
            flash(f'Error: {e}')
            db.session.rollback()

    return render_template('settings.html', user=user)


# Route for logout
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
