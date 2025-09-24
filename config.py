# config.py - Updated for WS281X LED Ring Integration

SYSTEM_NAME = "MOTORPASS"
SYSTEM_VERSION = "1.5"  

# =============================================================================
# 🛠️ SIMPLE DEV MODE - Just change True/False
# =============================================================================
ENABLE_BUZZER = False    # Set to False to disable buzzer
ENABLE_LED = True        # Set to True for WS281X LED Ring

# =============================================================================
# FILE PATHS CONFIGURATION - Centralized JSON file paths
# =============================================================================
# JSON Database Files
FINGERPRINT_DATA_FILE = "json_folder/fingerprint_database.json"
ADMIN_DATA_FILE = "json_folder/admin_database.json"
ADMIN_ROLES_FILE = "json_folder/admin_roles.json"

# =============================================================================
# CAMERA CONFIGURATION - RPi Camera 3 Only
# =============================================================================
USE_RPI_CAMERA = True  # Always True - no fallback
RPI_CAMERA_RESOLUTION = (1280, 720)  # HD resolution for RPi Camera 3
RPI_CAMERA_FRAMERATE = 50
RPI_CAMERA_WARMUP_TIME = 1  # seconds

# =============================================================================
# WS281X LED RING CONFIGURATION
# =============================================================================
WS281X_CONFIG = {
    'LED_COUNT': 12,         # Number of LEDs in ring
    'LED_PIN': 18,           # GPIO pin (must support PWM)
    'LED_FREQ_HZ': 800000,   # LED signal frequency in Hz
    'LED_DMA': 10,           # DMA channel to use
    'LED_BRIGHTNESS': 76,    # LED brightness (0-255)
    'LED_INVERT': False,     # Invert the signal
    'LED_CHANNEL': 0,        # PWM channel (0 or 1)
}

# LED State Colors (R, G, B)
LED_COLORS = {
    'READY': (0, 0, 255),        # Blue - system ready
    'SCANNING': (255, 255, 0),   # Yellow - fingerprint scanning
    'PROCESSING': (255, 165, 0), # Orange - processing data
    'SUCCESS': (0, 255, 0),      # Green - operation successful
    'FAILED': (255, 0, 0),       # Red - operation failed
    'CAMERA': (255, 255, 255),   # White - camera active
    'OFF': (0, 0, 0)             # Off - no light
}

# =============================================================================
# HARDWARE PIN CONFIGURATION (Legacy - kept for compatibility)
# =============================================================================
HARDWARE_PINS = {
    'LED_RED_PIN': 18,      # Now used for WS281X data pin
    'LED_GREEN_PIN': 16,    # Legacy - not used with WS281X
    'BUZZER_PIN': 22
}

# =============================================================================
# MENU CONFIGURATIONS
# =============================================================================
MAIN_MENU = {
    'title': f"🚗 {SYSTEM_NAME} - VERIFICATION SYSTEM",
    'options': [
        "👨‍💼 1️⃣  ADMIN - Manage System",
        "🎓👔 2️⃣  STUDENT/STAFF - Verify License & Time Tracking", 
        "👤 3️⃣  GUEST - Quick Verification",
        "🚪 4️⃣  EXIT"
    ]
}

ADMIN_MENU = {
    'title': f"🔧 {SYSTEM_NAME} - ADMIN PANEL",
    'options': [
        "1️⃣  Enroll New User (Student/Staff ID + Fingerprint)",
        "2️⃣  View Enrolled Users",
        "3️⃣  Delete User Fingerprint", 
        "4️⃣  Reset All Data",
        "5️⃣  Sync Student/Staff Database",
        "6️⃣  View Time Records",
        "7️⃣  Clear Time Records",
        "8️⃣  Back to Main Menu"
    ]
}

# =============================================================================
# SYSTEM REQUIREMENTS NOTICE
# =============================================================================
LED_REQUIREMENTS_MESSAGE = """
🌟 WS281X LED Ring Requirements:
• Run with sudo: sudo ~/myvenv/bin/python3 main.py
• Install library: sudo pip install rpi_ws281x
• Use PWM-capable GPIO pin (default: GPIO 18)
• Connect: Data->GPIO18, +5V->5V, GND->GND
"""
