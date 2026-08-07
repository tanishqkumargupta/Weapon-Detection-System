from flask import Response
from camera import generate_frames
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from db_models import db, User, Detection
import os
import cv2

from detector import detect
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
RESULT_FOLDER = "static/results"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["RESULT_FOLDER"] = RESULT_FOLDER

app.config["SECRET_KEY"] = "wds-secret-key"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///wds.db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

bcrypt = Bcrypt(app)

with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        username = request.form["username"].strip()

        email = request.form["email"].strip().lower()

        password = request.form["password"]

        confirm = request.form["confirmPassword"]

        if password != confirm:

            flash("Passwords do not match")

            return redirect(url_for("signup"))

        existing = User.query.filter(
            (User.username == username) |
            (User.email == email)
        ).first()

        if existing:

            flash("User already exists")

            return redirect(url_for("signup"))

        hashed = bcrypt.generate_password_hash(password).decode("utf-8")

        user = User(
            username=username,
            email=email,
            password=hashed
        )

        db.session.add(user)

        db.session.commit()

        flash("Registration Successful")

        return redirect(url_for("login"))

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]

        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):

            session["user_id"] = user.id

            session["username"] = user.username

            return redirect(url_for("dashboard"))

        flash("Invalid Credentials")

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect(url_for("login"))

    total = Detection.query.count()

    latest = Detection.query.order_by(
        Detection.timestamp.desc()
    ).first()

    if latest:
        latest_threat = latest.threat
        latest_confidence = round(latest.confidence * 100, 2)
    else:
        latest_threat = "None"
        latest_confidence = 0

    # NOTE (frontend modernization): added to power the "Recent
    # Detections" panel on the redesigned dashboard. Uses the existing
    # Detection model/table only -- no schema or route changes.
    recent = Detection.query.order_by(
        Detection.timestamp.desc()
    ).limit(5).all()

    return render_template(
        "dashboard.html",
        username=session["username"],
        total=total,
        latest_threat=latest_threat,
        latest_confidence=latest_confidence,
        recent=recent
    )


@app.route("/camera", methods=["GET", "POST"])
def camera():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        camera_type = request.form["camera_type"]
        camera_url = request.form.get("camera_url", "").strip()

        if camera_type == "ip" and camera_url == "":
            flash("Please enter an IP camera URL.")
            return redirect(url_for("camera"))

        session["camera_type"] = camera_type
        session["camera_url"] = camera_url

        return redirect(url_for("camera"))

    return render_template("camera.html")



@app.route("/upload", methods=["GET", "POST"])
def upload():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        file = request.files.get("image")

        if file is None or file.filename == "":
            flash("Please select an image.")
            return redirect(url_for("upload"))

        filename = secure_filename(file.filename)

        upload_path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            filename
        )

        file.save(upload_path)

        image = cv2.imread(upload_path)

        rendered, detections = detect(image)

        for item in detections:

            detection = Detection(
                filename=filename,
                threat=item["class"],
                confidence=item["confidence"],
                source="Image Upload"
            )

            db.session.add(detection)

        db.session.commit()

        result_name = "result_" + filename

        result_path = os.path.join(
            app.config["RESULT_FOLDER"],
            result_name
        )

        cv2.imwrite(result_path, rendered)

        return render_template(
            "upload.html",
            image=url_for(
                "static",
                filename="results/" + result_name
            ),
            detections=detections
        )

    return render_template(
        "upload.html",
        image=None,
        detections=None
    )


@app.route("/history")
def history():

    if "user_id" not in session:
        return redirect(url_for("login"))

    detections = Detection.query.order_by(
        Detection.timestamp.desc()
    ).all()

    return render_template(
        "history.html",
        detections=detections
    )


@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")

@app.route("/video_feed")
def video_feed():

    source = 0

    if session.get("camera_type") == "ip":

        source = session.get("camera_url")

    return Response(
        generate_frames(app, source),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )