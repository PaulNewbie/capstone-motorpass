# etc/services/fingerprint.py - FINAL CLEAN - NO DUPLICATES

import time
import serial
import adafruit_fingerprint
import tkinter as tk
from tkinter import simpledialog, messagebox
import threading

# Import database operations
from database.db_operations import (
    get_user_by_id,
    record_time_attendance
)

# Import from utils
from etc.utils.json_database import (
    load_fingerprint_database,
    save_fingerprint_database,
    load_admin_database,
    safe_get_student_by_id,
    safe_get_staff_by_id
)

from etc.services.hardware.buzzer_control import play_failure

# =================== HARDWARE SETUP ===================
uart = serial.Serial("/dev/ttyS0", baudrate=57600, timeout=1)
finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)

# =================== FOR ADMIN AUTHENTICATION ===================

def authenticate_admin_with_role(max_attempts=2, main_window=None):  # CHANGED: 3 -> 2
    """Authenticate admin and return role - FOR ADMIN BUTTON ONLY"""
    from etc.ui.fingerprint_gui import AdminFingerprintGUI
    
    print(f"\n🔐 ADMIN PANEL AUTHENTICATION")
    
    try:
        admin_gui = AdminFingerprintGUI(parent_window=main_window)
        authenticated_role = None
        
        def run_auth():
            nonlocal authenticated_role
            attempts = 0
            
            while attempts < max_attempts:
                attempts += 1
                print(f"Admin attempt {attempts}/{max_attempts}")
                
                admin_gui.root.after(0, lambda: admin_gui.update_status(f"👆 Place admin finger... (Attempt {attempts}/{max_attempts})", "#3498db"))
                
                # Wait for finger and process
                finger_detected = False
                for _ in range(100):  # 10 second timeout
                    try:
                        if finger.get_image() == adafruit_fingerprint.OK:
                            finger_detected = True
                            break
                    except:
                        pass
                    time.sleep(0.1)
                
                if not finger_detected:
                    if attempts < max_attempts:
                        admin_gui.root.after(0, lambda: admin_gui.update_status("⏰ Timeout! Try again...", "#e67e22"))
                        time.sleep(2)
                        continue
                    else:
                        # ADDED: Trigger buzzer alarm on final failure
                        play_failure()
                        admin_gui.root.after(0, admin_gui.show_failed)
                        return
                
                # Process fingerprint
                admin_gui.root.after(0, lambda: admin_gui.update_status("🔄 Processing...", "#f39c12"))
                
                try:
                    if finger.image_2_tz(1) != adafruit_fingerprint.OK:
                        if attempts < max_attempts:
                            admin_gui.root.after(0, lambda: admin_gui.update_status("❌ Processing failed! Try again...", "#e74c3c"))
                            time.sleep(2)
                            continue
                        else:
                            # ADDED: Trigger buzzer alarm on final failure
                            play_failure()
                            admin_gui.root.after(0, admin_gui.show_failed)
                            return
                except:
                    if attempts < max_attempts:
                        admin_gui.root.after(0, lambda: admin_gui.update_status("❌ Sensor error! Try again...", "#e74c3c"))
                        time.sleep(2)
                        continue
                    else:
                        # ADDED: Trigger buzzer alarm on final failure
                        play_failure()
                        admin_gui.root.after(0, admin_gui.show_failed)
                        return
                
                # Search for fingerprint
                admin_gui.root.after(0, lambda: admin_gui.update_status("🔍 Searching...", "#9b59b6"))
                
                try:
                    if finger.finger_search() != adafruit_fingerprint.OK:
                        if attempts < max_attempts:
                            admin_gui.root.after(0, lambda: admin_gui.update_status("❌ No match found! Try again...", "#e74c3c"))
                            time.sleep(2)
                            continue
                        else:
                            # ADDED: Trigger buzzer alarm on final failure
                            play_failure()
                            admin_gui.root.after(0, admin_gui.show_failed)
                            return
                except:
                    if attempts < max_attempts:
                        admin_gui.root.after(0, lambda: admin_gui.update_status("❌ Search failed! Try again...", "#e74c3c"))
                        time.sleep(2)
                        continue
                    else:
                        # ADDED: Trigger buzzer alarm on final failure
                        play_failure()
                        admin_gui.root.after(0, admin_gui.show_failed)
                        return
                
                matched_slot = str(finger.finger_id)
                
                # SIMPLE SLOT-BASED ACCESS CONTROL
                if matched_slot == "1":
                    # Slot 1 = Super Admin
                    try:
                        admin_db = load_admin_database()
                        user_name = admin_db.get("1", {}).get("name", "Super Admin")
                    except:
                        user_name = "Super Admin"
                    
                    authenticated_role = "super_admin"
                    print(f"✅ Super Admin authenticated: {user_name} (Slot 1)")
                    
                elif matched_slot == "2":
                    # Slot 2 = Guard
                    try:
                        fingerprint_db = load_fingerprint_database()
                        user_name = fingerprint_db.get("2", {}).get("name", "Guard User")
                    except:
                        user_name = "Guard User"
                    
                    authenticated_role = "guard"
                    print(f"✅ Guard authenticated: {user_name} (Slot 2)")
                    
                else:
                    # All other slots = Check if they exist and are staff
                    try:
                        fingerprint_db = load_fingerprint_database()
                        
                        if matched_slot not in fingerprint_db:
                            if attempts < max_attempts:
                                admin_gui.root.after(0, lambda: admin_gui.update_status("❌ User not enrolled! Try again...", "#e74c3c"))
                                time.sleep(2)
                                continue
                            else:
                                # ADDED: Trigger buzzer alarm on final failure
                                play_failure()
                                admin_gui.root.after(0, admin_gui.show_failed)
                                return
                        
                        finger_info = fingerprint_db[matched_slot]
                        user_type = finger_info.get('user_type')
                        user_name = finger_info.get('name', 'Unknown')
                        
                        # Only STAFF can access admin panel (not students)
                        if user_type != 'STAFF':
                            if attempts < max_attempts:
                                admin_gui.root.after(0, lambda: admin_gui.update_status("❌ Only staff can access admin! Try again...", "#e74c3c"))
                                time.sleep(2)
                                continue
                            else:
                                # ADDED: Trigger buzzer alarm on final failure
                                play_failure()
                                admin_gui.root.after(0, admin_gui.show_failed)
                                return
                        
                        # All staff slots get super admin access
                        authenticated_role = "super_admin"
                        print(f"✅ Staff Admin authenticated: {user_name} (Slot {matched_slot})")
                        
                    except Exception as e:
                        print(f"❌ Database error: {e}")
                        if attempts < max_attempts:
                            admin_gui.root.after(0, lambda: admin_gui.update_status("❌ Database error! Try again...", "#e74c3c"))
                            time.sleep(2)
                            continue
                        else:
                            # ADDED: Trigger buzzer alarm on final failure
                            play_failure()
                            admin_gui.root.after(0, admin_gui.show_failed)
                            return
                
                print(f"🎯 Confidence: {finger.confidence}")
                admin_gui.root.after(0, admin_gui.show_success)
                return
            
            # All attempts failed - trigger alarm
            play_failure()
            admin_gui.root.after(0, admin_gui.show_failed)
        
        # Start authentication in thread
        auth_thread = threading.Thread(target=run_auth, daemon=True)
        auth_thread.start()
        
        # Wait for GUI to close
        admin_gui.root.wait_window()
        
        return authenticated_role
        
    except Exception as e:
        print(f"❌ GUI Error: {e}")
        return None

