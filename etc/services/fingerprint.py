# etc/services/fingerprint.py - CLEAN AND ORGANIZED

import time
import serial
import adafruit_fingerprint
import json
import os
import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
import threading

# Import database operations
from database.db_operations import (
    get_user_by_id,
    get_student_time_status,
    record_time_in,
    record_time_out,
    record_time_attendance,
    get_all_time_records,
    clear_all_time_records,
    get_students_currently_in,
    get_student_by_id,
    get_staff_by_id,
    get_all_students,
    get_all_staff
)

# =================== HARDWARE SETUP ===================
uart = serial.Serial("/dev/ttyS0", baudrate=57600, timeout=1)
finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)

# File paths
FINGERPRINT_DATA_FILE = "json_folder/fingerprint_database.json"
ADMIN_DATA_FILE = "json_folder/admin_database.json"
ADMIN_ROLES_FILE = "json_folder/admin_roles.json"

# =================== JSON DATABASE FUNCTIONS ===================

def load_fingerprint_database():
    """Load fingerprint database"""
    if os.path.exists(FINGERPRINT_DATA_FILE):
        try:
            with open(FINGERPRINT_DATA_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_fingerprint_database(database):
    """Save fingerprint database"""
    os.makedirs(os.path.dirname(FINGERPRINT_DATA_FILE), exist_ok=True)
    with open(FINGERPRINT_DATA_FILE, 'w') as f:
        json.dump(database, f, indent=4)

def load_admin_database():
    """Load admin database"""
    if os.path.exists(ADMIN_DATA_FILE):
        try:
            with open(ADMIN_DATA_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_admin_database(database):
    """Save admin database"""
    os.makedirs(os.path.dirname(ADMIN_DATA_FILE), exist_ok=True)
    with open(ADMIN_DATA_FILE, 'w') as f:
        json.dump(database, f, indent=4)

def load_admin_roles():
    """Load admin roles database"""
    if os.path.exists(ADMIN_ROLES_FILE):
        try:
            with open(ADMIN_ROLES_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_admin_roles(roles_db):
    """Save admin roles database"""
    os.makedirs(os.path.dirname(ADMIN_ROLES_FILE), exist_ok=True)
    with open(ADMIN_ROLES_FILE, 'w') as f:
        json.dump(roles_db, f, indent=4)

# =================== DATABASE COMPATIBILITY FUNCTIONS ===================

def safe_get_student_by_id(student_id):
    """Safely get student by ID with fallback"""
    try:
        return get_student_by_id(student_id)
    except:
        try:
            result = get_user_by_id(student_id)
            if result and result.get('user_type') == 'STUDENT':
                return result
        except:
            pass
        return None

def safe_get_staff_by_id(staff_id):
    """Safely get staff by ID with fallback"""
    try:
        return get_staff_by_id(staff_id)
    except:
        try:
            result = get_user_by_id(staff_id)
            if result and result.get('user_type') == 'STAFF':
                return result
        except:
            pass
        return None

# =================== ADMIN AUTHENTICATION - GUI ONLY ===================

def authenticate_admin(max_attempts=3, parent_window=None):
    """Authenticate admin using fingerprint with GUI - FOR VIP BUTTON"""
    from etc.ui.fingerprint_gui import AdminFingerprintGUI
    
    print(f"\n🔐 ADMIN AUTHENTICATION")
    
    try:
        admin_gui = AdminFingerprintGUI(parent_window=parent_window)
        
        def run_auth():
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
                            admin_gui.root.after(0, admin_gui.show_failed)
                            return
                except:
                    if attempts < max_attempts:
                        admin_gui.root.after(0, lambda: admin_gui.update_status("❌ Sensor error! Try again...", "#e74c3c"))
                        time.sleep(2)
                        continue
                    else:
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
                            admin_gui.root.after(0, admin_gui.show_failed)
                            return
                except:
                    if attempts < max_attempts:
                        admin_gui.root.after(0, lambda: admin_gui.update_status("❌ Search failed! Try again...", "#e74c3c"))
                        time.sleep(2)
                        continue
                    else:
                        admin_gui.root.after(0, admin_gui.show_failed)
                        return
                
                # Check if matched fingerprint is admin (slot 1)
                if finger.finger_id == 1:
                    try:
                        admin_db = load_admin_database()
                        admin_name = admin_db.get("1", {}).get("name", "Admin User")
                        print(f"✅ Welcome Admin: {admin_name}")
                        print(f"🎯 Confidence: {finger.confidence}")
                        admin_gui.root.after(0, admin_gui.show_success)
                        return
                    except:
                        admin_gui.root.after(0, admin_gui.show_success)
                        return
                else:
                    if attempts < max_attempts:
                        admin_gui.root.after(0, lambda: admin_gui.update_status("❌ Not admin fingerprint! Try again...", "#e74c3c"))
                        time.sleep(2)
                        continue
                    else:
                        admin_gui.root.after(0, admin_gui.show_failed)
                        return
            
            # All attempts failed
            admin_gui.root.after(0, admin_gui.show_failed)
        
        # Start authentication in thread
        auth_thread = threading.Thread(target=run_auth, daemon=True)
        auth_thread.start()
        
        # Wait for GUI to close
        admin_gui.root.wait_window()
        
        # Return result
        result = admin_gui.auth_result
        if result:
            print("✅ Admin authentication successful!")
        else:
            print("❌ Admin authentication failed!")
        
        return result
        
    except Exception as e:
        print(f"❌ Admin authentication error: {e}")
        return False

def authenticate_admin_with_role(max_attempts=3, main_window=None):
    """Authenticate admin and return role - FOR ADMIN BUTTON"""
    from etc.ui.fingerprint_gui import AdminFingerprintGUI
    
    print(f"\n🔐 ADMIN AUTHENTICATION")
    
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
                            admin_gui.root.after(0, admin_gui.show_failed)
                            return
                except:
                    if attempts < max_attempts:
                        admin_gui.root.after(0, lambda: admin_gui.update_status("❌ Sensor error! Try again...", "#e74c3c"))
                        time.sleep(2)
                        continue
                    else:
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
                            admin_gui.root.after(0, admin_gui.show_failed)
                            return
                except:
                    if attempts < max_attempts:
                        admin_gui.root.after(0, lambda: admin_gui.update_status("❌ Search failed! Try again...", "#e74c3c"))
                        time.sleep(2)
                        continue
                    else:
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
                            admin_gui.root.after(0, admin_gui.show_failed)
                            return
                
                print(f"🎯 Confidence: {finger.confidence}")
                admin_gui.root.after(0, admin_gui.show_success)
                return
            
            # All attempts failed
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

# =================== ADMIN SETUP FUNCTIONS ===================

def check_admin_fingerprint_exists():
    """Check if admin fingerprint is enrolled in slot 1"""
    try:
        if finger.read_templates() != adafruit_fingerprint.OK:
            return False
        admin_db = load_admin_database()
        return "1" in admin_db
    except:
        return False

def enroll_admin_fingerprint():
    """Enroll admin fingerprint (Super Admin)"""
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

    print(f"💾 Storing...", end="")
    if finger.store_model(1) == adafruit_fingerprint.OK:
        print("✅")
        
        # Save super admin info
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

# =================== USER ENROLLMENT FUNCTIONS ===================

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
            if not messagebox.askyesno("User Not Found", 
                f"User ID '{user_id}' not found.\n\nTry again?"):
                root.destroy()
                return None

def find_next_available_slot():
    """Find next available slot (skips slot 1 for admin)"""
    try:
        if finger.read_templates() != adafruit_fingerprint.OK:
            print("❌ Failed to read sensor templates")
            return None
        
        database = load_fingerprint_database()
        
        for slot in range(2, finger.library_size + 1):
            if str(slot) not in database:
                print(f"🎯 Auto-assigned slot: #{slot}")
                return slot
        
        print("❌ No available slots found")
        return None
        
    except Exception as e:
        print(f"❌ Error finding available slot: {e}")
        return None

def enroll_finger_with_user_info(location=None):
    """Enhanced enrollment using Student ID or Staff No"""
    if location is None:
        location = find_next_available_slot()
        if location is None:
            print("❌ No available slots for enrollment")
            return False
    
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
        print("✅")

        print("🔄 Processing...", end="")
        if finger.image_2_tz(fingerimg) != adafruit_fingerprint.OK:
            print("❌ Failed")
            return False
        print("✅")

        if fingerimg == 1:
            print("✋ Remove finger")
            time.sleep(1)
            while finger.get_image() == adafruit_fingerprint.OK:
                pass
    
    # Create and store template
    print("🔄 Creating template...", end="")
    if finger.create_model() != adafruit_fingerprint.OK:
        print("❌ Failed")
        return False
    print("✅")
    
    print(f"💾 Storing at slot #{location}...", end="")
    if finger.store_model(location) != adafruit_fingerprint.OK:
        print("❌ Failed")
        return False
    print("✅")
    
    # Save to database
    database = load_fingerprint_database()
    
    database[str(location)] = {
        "name": user_info['full_name'],
        "user_type": user_info['user_type'],
        "enrolled_date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "slot": location
    }
    
    # Add type-specific information
    if user_info['user_type'] == 'STUDENT':
        database[str(location)].update({
            "student_id": user_info['student_id'],
            "unified_id": user_info['student_id'],
            "course": user_info['course']
        })
    else:
        database[str(location)].update({
            "staff_no": user_info['staff_no'],
            "unified_id": user_info['staff_no'],
            "staff_role": user_info['staff_role']
        })
    
    save_fingerprint_database(database)
    print(f"🎉 Enrollment successful: {user_info['full_name']} (Slot #{location})")
    return True

# =================== FINGERPRINT MANAGEMENT ===================

def delete_fingerprint(finger_id):
    """Delete fingerprint from sensor and database"""
    try:
        if finger.delete_model(finger_id) != adafruit_fingerprint.OK:
            print(f"❌ Failed to delete fingerprint #{finger_id} from sensor")
            return False
        
        database = load_fingerprint_database()
        if str(finger_id) in database:
            user_name = database[str(finger_id)].get('name', 'Unknown')
            del database[str(finger_id)]
            save_fingerprint_database(database)
            print(f"✅ Deleted fingerprint #{finger_id} ({user_name})")
            return True
        else:
            print(f"⚠️ Fingerprint #{finger_id} not found in database")
            return False
            
    except Exception as e:
        print(f"❌ Error deleting fingerprint: {e}")
        return False

def get_enrolled_users():
    """Get list of all enrolled users"""
    try:
        database = load_fingerprint_database()
        users = []
        
        for slot_id, user_data in database.items():
            if slot_id == "1":  # Skip admin
                continue
                
            users.append({
                "slot": int(slot_id),
                "name": user_data.get('name', 'Unknown'),
                "user_type": user_data.get('user_type', 'UNKNOWN'),
                "user_id": user_data.get('unified_id', user_data.get('student_id', user_data.get('staff_no', 'N/A'))),
                "enrolled_date": user_data.get('enrolled_date', 'Unknown')
            })
        
        users.sort(key=lambda x: x['slot'])
        return users
        
    except Exception as e:
        print(f"❌ Error getting enrolled users: {e}")
        return []

def view_enrolled_users():
    """Display all enrolled users"""
    users = get_enrolled_users()
    
    if not users:
        print("📝 No users enrolled yet")
        return
    
    print(f"\n📋 ENROLLED USERS ({len(users)} total)")
    print("=" * 70)
    print(f"{'Slot':<6} {'Name':<25} {'Type':<8} {'ID':<15} {'Enrolled':<15}")
    print("-" * 70)
    
    for user in users:
        print(f"{user['slot']:<6} {user['name'][:24]:<25} {user['user_type']:<8} {user['user_id']:<15} {user['enrolled_date'][:10]:<15}")
    
    print("=" * 70)

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

