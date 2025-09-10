# etc/utils/hardware_utils.py - Hardware Utility Functions

import os
import serial
import adafruit_fingerprint

# Import JSON database utilities
from etc.utils.json_database import load_fingerprint_database, load_admin_database

# Hardware setup (this will be imported from fingerprint.py)
# We'll access the finger object through parameter passing
uart = serial.Serial("/dev/ttyS0", baudrate=57600, timeout=1)
finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)

# =================== SENSOR UTILITY FUNCTIONS ===================

def test_sensor_connection():
    """Test fingerprint sensor connection"""
    try:
        print("\n🔍 Testing sensor connection...")
        
        if finger.read_templates() == adafruit_fingerprint.OK:
            print("✅ Sensor connection OK")
            print(f"📊 Templates stored: {finger.template_count}/{finger.library_size}")
            return True
        else:
            print("❌ Sensor connection failed")
            return False
            
    except Exception as e:
        print(f"❌ Sensor test error: {e}")
        return False

def init_fingerprint_service():
    """Initialize fingerprint service and check sensor"""
    print("🔧 Initializing fingerprint service...")
    
    try:
        if not test_sensor_connection():
            print("❌ Failed to initialize fingerprint sensor")
            return False
        
        # Create data directories
        os.makedirs("json_folder", exist_ok=True)
        os.makedirs("backups", exist_ok=True)
        
        # Check admin fingerprint
        if not check_admin_fingerprint_exists():
            print("⚠️ No admin fingerprint found - will need setup")
        
        print("✅ Fingerprint service initialized successfully")
        return True
        
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        return False

def check_admin_fingerprint_exists():
    """Check if admin fingerprint is enrolled in slot 1"""
    try:
        if finger.read_templates() != adafruit_fingerprint.OK:
            return False
        admin_db = load_admin_database()
        return "1" in admin_db
    except:
        return False

def find_next_available_slot():
    """Automatically find the next available slot (skips slot 1 for admin)"""
    try:
        # Read current templates from sensor
        if finger.read_templates() != adafruit_fingerprint.OK:
            print("❌ Failed to read sensor templates")
            return None
        
        # Load fingerprint database
        database = load_fingerprint_database()
        
        # Find next available slot starting from 2 (skip admin slot 1)
        for slot in range(2, finger.library_size + 1):
            if str(slot) not in database:
                print(f"🎯 Auto-assigned slot: #{slot}")
                return slot
        
        print("❌ No available slots found")
        return None
        
    except Exception as e:
        print(f"❌ Error finding available slot: {e}")
        return None
