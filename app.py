from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from db_models import db, User

app = Flask(__name__)

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

    return render_template(
        "dashboard.html",
        username=session["username"]
    )


@app.route("/camera", methods=["GET", "POST"])
def camera():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        session["camera_type"] = request.form["camera_type"]

        session["camera_url"] = request.form["camera_url"]

        return redirect(url_for("live"))

    return render_template("camera.html")

@app.route("/live")
def live():

    if "user_id" not in session:
        return redirect(url_for("login"))

    return """
    <h2>Live Detection</h2>

    <p>

    Camera configured successfully.

    </p>

    <p>

    YOLOv5 integration will appear here.

    </p>

    <a href='/dashboard'>

    Dashboard

    </a>
    """

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )