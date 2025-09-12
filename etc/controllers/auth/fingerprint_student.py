# etc/controllers/auth/fingerprint_student.py
# Student/Staff fingerprint authentication functions

import time
import serial
import adafruit_fingerprint
import tkinter as tk
from tkinter import simpledialog, messagebox

# Import database operations
from database.db_operations import (
    record_time_attendance
)


# =================== HARDWARE SETUP ===================
uart = serial.Serial("/dev/ttyS0", baudrate=57600, timeout=1)
finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)

# =================== STUDENT/STAFF AUTHENTICATION ===================

def authenticate_fingerprint(max_attempts=5):
    """Student/Staff fingerprint authentication with GUI"""
    print(f"\n🔒 Starting fingerprint authentication (Max attempts: {max_attempts})")
    
    from etc.ui.fingerprint_gui import FingerprintAuthGUI
    
    try:
        auth_gui = FingerprintAuthGUI(max_attempts)
        auth_gui.root.wait_window()
        
        if auth_gui.auth_result is False:
            print("❌ Authentication failed or cancelled")
            return None
        elif auth_gui.auth_result is None:
            print("❌ Authentication failed - no result")
            return None
        else:
            print(f"✅ Authentication successful: {auth_gui.auth_result['name']}")
            return auth_gui.auth_result
            
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return None

def authenticate_fingerprint_with_time_tracking():
    """Authenticate fingerprint and auto handle time in/out"""
    student_info = authenticate_fingerprint()
    
    if not student_info or student_info['student_id'] == 'N/A':
        return student_info
    
    time_status = record_time_attendance(student_info)
    print(f"🕒 {time_status}")
    
    return student_info
