# 🛡️ Weapon Detection System (WDS)

<div align="center">

AI-Powered Real-Time Weapon Detection using **YOLOv5**, **Flask**, **OpenCV**, and **PyTorch**

Detect weapons from uploaded images, webcams, and IP cameras while automatically logging events, storing evidence, and sending email alerts.

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-3.1-black?logo=flask)
![YOLOv5](https://img.shields.io/badge/YOLOv5-Computer%20Vision-red)
![PyTorch](https://img.shields.io/badge/PyTorch-2.x-ee4c2c?logo=pytorch)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-green?logo=opencv)
![SQLite](https://img.shields.io/badge/Database-SQLite-blue?logo=sqlite)
![License](https://img.shields.io/badge/License-MIT-green)

</div>

---

# 📌 Overview

Weapon Detection System (WDS) is an AI-powered computer vision application capable of detecting weapons in real time using a custom-trained YOLOv5 model.

The system supports multiple input sources including:

- 📷 Uploaded Images
- 🎥 Live Webcam
- 📱 Mobile IP Camera
- 📧 Automated Email Alerts

Whenever a weapon is detected, WDS:

- Detects and classifies the threat
- Draws bounding boxes
- Saves evidence snapshots
- Logs the event into a database
- Sends an email notification with the captured image

The project demonstrates the integration of Deep Learning, Computer Vision, Backend Development, and Web Technologies into a single end-to-end application.

---

# ✨ Features

## 🔐 Authentication

- User Registration
- Secure Login
- Password Hashing (Flask-Bcrypt)
- Session Management

---

## 🤖 AI Weapon Detection

- YOLOv5 Custom Model
- Real-Time Detection
- Confidence Scores
- Bounding Box Visualization
- Multi-Class Detection

Supported Sources:

- Image Upload
- Webcam
- IP Camera

---

## 📧 Smart Alerts

Automatic Email Notification

Includes:

- Threat Type
- Detection Confidence
- Detection Timestamp
- Snapshot Attachment

Email cooldown prevents repeated notifications for continuous detections.

---

## 📸 Snapshot Storage

Every detection automatically stores:

- Annotated image
- Timestamp
- Threat class
- Confidence score

Snapshots are available from the detection history.

---

## 📊 Dashboard

Interactive dashboard displaying:

- Recent detections
- Detection history
- Confidence values
- Threat information
- Image previews

---

## 📜 Detection History

Every event is permanently logged.

Stored Information:

- Threat Type
- Confidence
- Source
- Timestamp
- Snapshot

---

# 🏗️ System Architecture

```

Camera / Upload

↓

OpenCV

↓

YOLOv5 Model

↓

Weapon Detection

↓

Threat Mapping

↓

Snapshot Storage

↓

SQLite Database

↓

Dashboard

↓

Email Alert

```

---

# 🧠 Detection Pipeline

1. Capture image/frame
2. Preprocess using OpenCV
3. Perform inference using YOLOv5
4. Extract predictions
5. Filter detections
6. Draw bounding boxes
7. Save snapshot
8. Store detection in database
9. Send email alert
10. Display results on dashboard

---

# 🛠️ Tech Stack

| Category | Technology |
|------------|----------------|
| Language | Python |
| Backend | Flask |
| Computer Vision | OpenCV |
| AI Framework | PyTorch |
| Detection Model | YOLOv5 |
| Database | SQLite |
| ORM | SQLAlchemy |
| Authentication | Flask-Bcrypt |
| Email | SMTP |
| Frontend | HTML, CSS, JavaScript |

---

# 📁 Project Structure

```text
Weapon-Detection-System/
│
├── app.py
├── camera.py
├── detector.py
├── db_models.py
├── email_service.py
├── requirements.txt
├── .env.example
├── README.md
├── CHANGES.md
│
├── weights/
│   └── best.pt
│
├── uploads/
├── static/
├── templates/
├── wds_utils/
└── yolov5/
```

---

# 🚀 Installation

Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/weapon-detection-system.git

cd weapon-detection-system
```

Create Virtual Environment

```bash
python -m venv .venv
```

Activate

Windows

```bash
.venv\Scripts\activate
```

Linux / macOS

```bash
source .venv/bin/activate
```

Install Dependencies

```bash
pip install -r requirements.txt
```

---

# ⚙️ Environment Variables

Create a `.env`

```
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
ALERT_EMAIL=receiver_email@gmail.com
```

---

# ▶️ Run the Application

```bash
python app.py
```

Open

```
http://127.0.0.1:5000
```

---

# 📷 Supported Input Sources

## Image Upload

Upload an image and detect weapons.

---

## Webcam

Uses OpenCV to stream frames directly from the local webcam.

---

## IP Camera

Supports mobile IP camera streams.

Example:

```
http://192.168.x.x:8080/video
```

---

# 📧 Email Notification Workflow

Whenever a threat is detected:

- Snapshot is saved
- Detection is logged
- Email is generated
- Snapshot is attached
- Alert is sent to the configured recipient

---

# 🗃 Database Schema

## Users

| Field | Type |
|------------|-----------|
| id | Integer |
| username | String |
| email | String |
| password | String |

---

## Detections

| Field | Type |
|------------|-----------|
| id | Integer |
| filename | String |
| threat | String |
| confidence | Float |
| source | String |
| timestamp | DateTime |

---

# 📈 Future Improvements

- PostgreSQL Support
- Docker Deployment
- Cloud Storage
- Multi-Camera Monitoring
- REST API
- User Roles
- Analytics Dashboard
- SMS Notifications
- Telegram Alerts
- Mobile Application
- Cloud Deployment

---

# 📸 Screenshots

> Add screenshots inside:

```
docs/screenshots/
```

Recommended:

- Home Page
- Login
- Dashboard
- Upload Detection
- Webcam Detection
- IP Camera Detection
- Detection History
- Email Alert

---

# 📽 Demo

A short demonstration video or GIF can be added here.

---

# 🤝 Contributing

Contributions are welcome.

Feel free to fork the repository, open issues, or submit pull requests for improvements.

---

# 📄 License

This project is licensed under the MIT License.

---

# 👨‍💻 Author

**Tanishq Kumar Gupta**

Computer Science Engineering

Artificial Intelligence • Computer Vision • Full Stack Development

GitHub:
https://github.com/tanishqkumargupta

---

## ⭐ If you found this project useful, consider giving it a star!