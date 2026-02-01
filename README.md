# MotorPass: Intelligent Vehicle Access

![Python](https://img.shields.io/badge/Python-3.x-blue?style=flat&logo=python)
![Platform](https://img.shields.io/badge/Platform-Raspberry%20Pi-red?style=flat&logo=raspberrypi)
![AI Model](https://img.shields.io/badge/AI-ONNX-green?style=flat&logo=onnx)

**MotorPass** is a next-generation gatekeeping system designed to automate security. By fusing **Computer Vision**, **Biometrics**, and **Cloud Sync**, it creates a seamless, autonomous entry experience for modern institutions.

---

## The MotorPass Advantage

Manual logging is obsolete. MotorPass upgrades your security infrastructure:
* **🤖 Autonomous Entry:** AI makes the decisions, reducing human error.
* **🧬 Biometric Speed:** Students enter in seconds via fingerprint.
* **☁️ Real-Time Sync:** All entry logs are instantly pushed to the cloud.

---

## 🔮 Core Capabilities

### AI Computer Vision
* ** Neural Helmet Detection:** A custom-trained **ONNX** model analyzes video feeds in real-time. It intelligently distinguishes between safe (Full-face) and unsafe (Half-face) helmets, automatically denying entry to violators.
* ** Anti-Spoofing Logic:** Advanced algorithms filter out fake IDs and "Student Permits" during guest registration to ensure only valid licenses are processed.

### Smart Access Control
* ** Biometric Verification:** High-speed fingerprint authentication for registered personnel.
* ** Hybrid OCR Engine:**
    * **Online Mode:** Leverages cloud API power for precision text extraction.
    * **Offline Fallback:** Automatically switches to a local neural network (Tesseract) if the internet fails.

###  Data & Connectivity
* **🔥 Firebase Integration:** Live database synchronization for remote monitoring.
* ** Resilient Storage:** Maintains a local SQLite mirror to ensure 100% uptime, even during network outages.

---

## ⚙️ Hardware Architecture
Optimized for the **Raspberry Pi 4 / 5**.

1.  ** Vision:** Pi Camera Module / HD Webcam.
2.  ** Identity:** Optical Fingerprint Sensor (UART).
3.  ** Feedback:** RGB LED Matrix & Active Buzzer System.
4.  ** Compute:** Raspberry Pi (Hosting the AI Inference Engine).

---

## 💾 Installation Protocol

### 1. System Initialization
Ensure your Raspberry Pi environment is prepped with the required libraries:
```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr libtesseract-dev libatlas-base-dev python3-tk
```

### 2. Dependency Injection
Install the Python modules required for AI and Hardware control:

Bash
pip install -r .others/requirements_outside.txt

### 3. Configuration
🔑 API Keys: Navigate to etc/services/license_reader.py and inject your OCR.space API key.

Pin Mapping: Verify GPIO pin assignments in config.py match your physical wiring.

Deployment
Initialize hardware sensors.

Execute the main sequence:

Bash
python main.py
The Touch Interface will load. Select your operating mode (Student, Guest, Admin).

📂 Codebase Structure
main.py: System Core.

best.onnx:  Trained Neural Network Model.

etc/services/helmet_infer.py:  Vision Processing Logic.

etc/services/hardware/:  Hardware Drivers.

etc/ui/:  User Interface.

🤝 Credits
Capstone Project Development

Engine: Python 3 + OpenCV

AI: Custom YOLO/ONNX Architecture
