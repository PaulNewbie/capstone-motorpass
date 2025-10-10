# etc/controllers/auth/admin_auth.py

import time
import serial
import adafruit_fingerprint
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import threading

from etc.utils.json_database import *

from database.db_operations import (
    get_user_by_id,
    get_student_by_id,
    get_staff_by_id
)

from etc.utils.hardware_utils import finger, check_admin_fingerprint_exists

# =================== ADMIN ENROLLMENT FUNCTIONS ===================

def enroll_super_admin():
    """Enroll super admin fingerprint in slot 1"""
    print("\n🔐 ENROLL SUPER ADMIN FINGERPRINT")
    
    # Check if admin already exists
    try:
        admin_db = load_admin_database()
        if "1" in admin_db:
            print(f"⚠️  Super admin already exists: {admin_db['1'].get('name', 'Unknown')}")
            if input("Replace it? (y/N): ").lower() != 'y':
                print("❌ Cancelled.")
                return False
    except:
        pass
    
    # Get admin name
    admin_name = input("Enter super admin name: ").strip()
    if not admin_name:
        print("❌ Super admin name required.")
        return False
    
    print(f"👤 Enrolling super admin: {admin_name}")
    
    # Fingerprint enrollment process
    for fingerimg in range(1, 3):
        print(f"👆 Place finger {'(first time)' if fingerimg == 1 else '(again)'}...", end="")
        
        while finger.get_image() != adafruit_fingerprint.OK:
            print(".", end="")
        print("✅")

        print("🔄 Processing...", end="")
        if finger.image_2_tz(fingerimg) != adafruit_fingerprint.OK:
            print("❌ Failed")
            return False
        print("✅")

        if fingerimg == 1:
            print("✋ Remove finger")
            time.sleep(1)
            while finger.get_image() != adafruit_fingerprint.NOFINGER:
                pass

    print("🗝️ Creating model...", end="")
    if finger.create_model() != adafruit_fingerprint.OK:
        print("❌ Failed")
        return False
    print("✅")

    print(f"💾 Storing to slot 1...", end="")
    if finger.store_model(1) == adafruit_fingerprint.OK:
        print("✅")
        
        # Save admin info
        admin_db = load_admin_database()
        admin_db["1"] = {
            "name": admin_name,
            "role": "super_admin",
            "enrolled_date": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        save_admin_database(admin_db)
        
        # Save role mapping
        roles_db = load_admin_roles()
        roles_db["1"] = "super_admin"
        save_admin_roles(roles_db)
        
        print(f"🎉 Super admin enrolled: {admin_name}")
        return True
    else:
        print("❌ Storage failed")
        return False

def enroll_guard_admin():
    """Enroll guard admin fingerprint in slot 2"""
    print("\n🛡️ ENROLL GUARD ADMIN FINGERPRINT")
    
    # Check if guard already exists
    try:
        fingerprint_db = load_fingerprint_database()
        if "2" in fingerprint_db:
            print(f"⚠️  Guard admin already exists: {fingerprint_db['2'].get('name', 'Unknown')}")
            if input("Replace it? (y/N): ").lower() != 'y':
                print("❌ Cancelled.")
                return False
    except:
        pass
    
    # Get guard name
    guard_name = input("Enter guard admin name: ").strip()
    if not guard_name:
        print("❌ Guard admin name required.")
        return False
    
    print(f"👤 Enrolling guard admin: {guard_name}")
    
    # Fingerprint enrollment process
    for fingerimg in range(1, 3):
        print(f"👆 Place finger {'(first time)' if fingerimg == 1 else '(again)'}...", end="")
        
        while finger.get_image() != adafruit_fingerprint.OK:
            print(".", end="")
        print("✅")

        print("🔄 Processing...", end="")
        if finger.image_2_tz(fingerimg) != adafruit_fingerprint.OK:
            print("❌ Failed")
            return False
        print("✅")

        if fingerimg == 1:
            print("✋ Remove finger")
            time.sleep(1)
            while finger.get_image() != adafruit_fingerprint.NOFINGER:
                pass

    print("🗝️ Creating model...", end="")
    if finger.create_model() != adafruit_fingerprint.OK:
        print("❌ Failed")
        return False
    print("✅")

    print(f"💾 Storing to slot 2...", end="")
    if finger.store_model(2) == adafruit_fingerprint.OK:
        print("✅")
        
        # Save guard info to fingerprint database (for consistency with other users)
        fingerprint_db = load_fingerprint_database()
        fingerprint_db["2"] = {
            "name": guard_name,
            "user_type": "GUARD_ADMIN",
            "enrolled_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "slot": 2
        }
        save_fingerprint_database(fingerprint_db)
        
        # Also save to admin database for role mapping
        admin_db = load_admin_database()
        admin_db["2"] = {
            "name": guard_name,
            "role": "guard",
            "enrolled_date": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        save_admin_database(admin_db)
        
        # Save role mapping
        roles_db = load_admin_roles()
        roles_db["2"] = "guard"
        save_admin_roles(roles_db)
        
        print(f"🎉 Guard admin enrolled: {guard_name}")
        return True
    else:
        print("❌ Storage failed")
        return False

# =================== ADMIN AUTHENTICATION HELPERS ===================

def enroll_finger_with_user_info(location):
    """Enhanced enrollment using Student ID or Staff No - ONLY CALLED FROM ADMIN.PY"""
    print(f"\n🔒 Starting enrollment for slot #{location}")
    
    user_info = get_user_id_gui()
    if not user_info:
        print("❌ No user selected.")
        return False
    
    print(f"👤 Enrolling: {user_info['full_name']} ({user_info['user_type']})")
    
    # Fingerprint enrollment process
    for fingerimg in range(1, 3):
        print(f"👆 Place finger {'(first time)' if fingerimg == 1 else '(again)'}...", end="")
        
        while finger.get_image() != adafruit_fingerprint.OK:
            print(".", end="")
            time.sleep(0.1)
        print("✅")
        
        print("🔄 Processing image...", end="")
        if finger.image_2_tz(fingerimg) != adafruit_fingerprint.OK:
            print("❌ Failed!")
            return False
        print("✅")
        
        if fingerimg == 1:
            print("🔄 Remove finger and place again...")
            time.sleep(2)
            while finger.get_image() == adafruit_fingerprint.OK:
                time.sleep(0.1)
    
    # Create template
    print("🔄 Creating fingerprint template...", end="")
    if finger.create_model() != adafruit_fingerprint.OK:
        print("❌ Failed!")
        return False
    print("✅")
    
    # Store template
    print(f"💾 Storing template at slot #{location}...", end="")
    if finger.store_model(location) != adafruit_fingerprint.OK:
        print("❌ Failed!")
        return False
    print("✅")
    
    # Update JSON database
    database = load_fingerprint_database()
    
    # Create unified database entry for both students and staff
    enrollment_data = {
        "name": user_info['full_name'],
        "user_type": user_info['user_type'],
        "unified_id": user_info.get('student_id') or user_info.get('staff_no'),
        "license_number": user_info['license_number'],
        "license_expiration": user_info['expiration_date'],
        "plate_number": user_info['plate_number'],
        "enrolled_date": time.strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # Add type-specific fields
    if user_info['user_type'] == 'STUDENT':
        enrollment_data.update({
            "student_id": user_info['student_id'],
            "course": user_info['course']
        })
    else:  # STAFF
        enrollment_data.update({
            "staff_no": user_info['staff_no'],
            "staff_role": user_info['staff_role']
        })
    
    database[str(location)] = enrollment_data
    save_fingerprint_database(database)
    
    print(f"✅ User enrolled successfully!")
    print(f"📋 Name: {user_info['full_name']}")
    print(f"🆔 ID: {enrollment_data['unified_id']}")
    print(f"🔢 Slot: #{location}")
    
    return True
    
def get_user_id_gui():
    """Get user ID via GUI and fetch info"""
    root = tk.Tk()
    root.withdraw()
    
    while True:
        user_id = simpledialog.askstring("User Enrollment", 
                                        "Enter Student No. or Staff No.:")
        
        if not user_id:
            root.destroy()
            return None
        
        user_id = user_id.strip()
        user_info = get_user_by_id(user_id)
        
        if user_info:
            if user_info['user_type'] == 'STUDENT':
                confirmation_message = f"""
Student Information Found:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👤 Name: {user_info['full_name']}
🆔 Student No.: {user_info['student_id']}
📚 Course: {user_info['course']}
🪪 License No.: {user_info['license_number']}
📅 License Exp.: {user_info['expiration_date']}
🏍️ Plate No.: {user_info['plate_number']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Proceed with fingerprint enrollment?
            """
            else:
                confirmation_message = f"""
Staff Information Found:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👤 Name: {user_info['full_name']}
🆔 Staff No.: {user_info['staff_no']}
👔 Role: {user_info['staff_role']}
🪪 License No.: {user_info['license_number']}
📅 License Exp.: {user_info['expiration_date']}
🏍️ Plate No.: {user_info['plate_number']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Proceed with fingerprint enrollment?
            """
            
            if messagebox.askyesno("Confirm User Information", confirmation_message):
                root.destroy()
                return user_info
        else:
            # User not found - this else block is now properly aligned
            if not messagebox.askyesno("User Not Found", 
                f"User ID '{user_id}' not found.\n\nTry again?"):
                root.destroy()
                return None
