# MotorPass — Intelligent Vehicle Access Control

![Python](https://img.shields.io/badge/Python-3.x-blue?style=flat&logo=python)
![Platform](https://img.shields.io/badge/Platform-Raspberry%20Pi-red?style=flat&logo=raspberrypi)
![AI Model](https://img.shields.io/badge/AI-ONNX%20%2F%20YOLO-green?style=flat&logo=onnx)
![Database](https://img.shields.io/badge/Database-Firebase%20%2B%20SQLite-orange?style=flat&logo=firebase)

MotorPass is a capstone project that automates vehicle access control using computer vision, biometric authentication, and cloud synchronization. Built for institutional deployment on Raspberry Pi, it replaces manual security logging with an AI-driven entry pipeline — detecting helmet compliance in real time, verifying identities via fingerprint, and syncing all records to the cloud.

---

## Table of Contents

- [Features](#features)
- [Hardware Requirements](#hardware-requirements)
- [Software Prerequisites](#software-prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the System](#running-the-system)
- [Project Structure](#project-structure)
- [Credits](#credits)

---

## Features

### Computer Vision

- **Helmet Compliance Detection** — A custom-trained ONNX (YOLO architecture) model analyzes the live camera feed and classifies helmets as full-face (compliant) or half-face (non-compliant), automatically denying entry to violations.
- **Anti-Spoofing for Guest Registration** — OCR validation logic filters out fake IDs and student permits during guest registration, ensuring only valid government-issued licenses are accepted.

### Access Control

- **Fingerprint Authentication** — High-speed biometric verification for registered students and personnel via an optical fingerprint sensor over UART.
- **Hybrid OCR Engine** — Extracts text from ID documents using OCR.space (cloud) as the primary method, with automatic fallback to a local Tesseract model when the network is unavailable.

### Data and Connectivity

- **Firebase Sync** — Entry logs and access events are pushed to a Firebase Realtime Database for remote monitoring.
- **Offline Resilience** — A local SQLite mirror maintains full system operation during network outages, syncing once connectivity is restored.

---

## Hardware Requirements

Tested and optimized for **Raspberry Pi 4 / 5**.

| Component | Purpose |
|---|---|
| Raspberry Pi 4 or 5 | Main compute unit and AI inference engine |
| Pi Camera Module or HD Webcam | Real-time video feed for helmet detection |
| Optical Fingerprint Sensor (UART) | Biometric identity verification |
| RGB LED Matrix | Visual access feedback (granted / denied) |
| Active Buzzer | Audio access feedback |

---

## Software Prerequisites

Before installation, update your Raspberry Pi and install the required system libraries:

```bash
sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get install -y tesseract-ocr libtesseract-dev libatlas-base-dev python3-tk
```

Verify Tesseract is installed correctly:

```bash
tesseract --version
```

---

## Installation

### 1. Clone the Repository

```bash
git clone <your-github-repo-url>
cd motorpass
```

### 2. Install Python Dependencies

```bash
pip install -r .others/requirements_outside.txt
```

> If you encounter permission errors, use `pip install --user -r .others/requirements_outside.txt` or run inside a virtual environment.

---

## Configuration

Before running the system, complete the following configuration steps.

### OCR.space API Key

Open `etc/services/license_reader.py` and replace the placeholder with your OCR.space API key:

```python
OCR_API_KEY = 'your_ocr_space_api_key_here'
```

You can obtain a free API key at [ocr.space](https://ocr.space/ocrapi).

### Firebase Credentials

Place your Firebase service account JSON file in the project root (or the path referenced in your config), and ensure `config.py` points to it correctly.

### GPIO Pin Mapping

Open `config.py` and verify that the GPIO pin assignments match your physical wiring for the fingerprint sensor, LED matrix, and buzzer. Mismatched pin assignments are the most common cause of hardware not responding on first boot.

---

## Running the System

Once hardware is connected and configuration is complete, launch the application:

```bash
python main.py
```

The touch interface will load. Select an operating mode:

- **Student** — Fingerprint-based entry for registered students.
- **Guest** — OCR-based license verification for unregistered visitors.
- **Admin** — System management and configuration panel.

---

## Project Structure

```
motorpass/
├── main.py                       # Application entry point and system orchestrator
├── config.py                     # GPIO pin assignments and global configuration
├── best.onnx                     # Trained YOLO helmet detection model
├── etc/
│   ├── services/
│   │   ├── helmet_infer.py       # ONNX inference and vision processing logic
│   │   ├── license_reader.py     # Hybrid OCR engine (cloud + Tesseract fallback)
│   │   ├── fingerprint.py        # Fingerprint sensor interface (UART)
│   │   └── hardware/             # Low-level drivers for LED, buzzer, and GPIO
│   └── ui/                       # Touch interface screens and UI components
├── db/
│   └── motorpass.db              # Local SQLite mirror database
├── .others/
│   └── requirements_outside.txt  # Python dependency list
└── README.md
```

---

## Credits

Developed as a capstone project.

| Component | Technology |
|---|---|
| Runtime | Python 3 |
| Computer Vision | OpenCV |
| AI Model | Custom YOLO trained and exported to ONNX |
| OCR | OCR.space API + Tesseract (offline fallback) |
| Cloud Database | Firebase Realtime Database |
| Local Database | SQLite |
| Hardware Platform | Raspberry Pi 4 / 5 |
