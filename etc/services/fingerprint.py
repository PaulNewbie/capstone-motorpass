# =================== ADMIN AUTHENTICATION WITH GUI ===================

class AdminFingerprintGUI:
    """Simple Admin Fingerprint Authentication GUI"""
    
    def __init__(self, parent_window=None):
        self.auth_result = False
        self.parent_window = parent_window
        
        # Create main window
        self.root = tk.Toplevel(parent_window)  # Make it a child of parent window
        self.root.title("Admin Authentication")
        self.root.geometry("350x250")
        self.root.configure(bg='#2c3e50')
        self.root.resizable(False, False)
        
        # Keep main window visible in background
        if parent_window:
            # Don't withdraw parent, just bring this window to front
            self.root.transient(parent_window)  # Set as child of main window
            self.root.grab_set()  # Make modal but keep parent visible
        
        # Center window on top of parent
        self.center_window()
        
        # Bring to front but don't hide parent
        self.root.lift()
        self.root.focus_force()
        
        # Create GUI elements
        self.create_widgets()
    
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def create_widgets(self):
        """Create admin authentication widgets"""
        # Title
        title_frame = tk.Frame(self.root, bg='#2c3e50')
        title_frame.pack(pady=15)
        
        tk.Label(title_frame, text="🔐 Admin Authentication", 
                font=("Arial", 16, "bold"), fg="#e74c3c", bg='#2c3e50').pack()
        
        # Main content frame
        content_frame = tk.Frame(self.root, bg='#34495e', relief='ridge', bd=2)
        content_frame.pack(padx=20, pady=10, fill='both', expand=True)
        
        # Admin icon
        tk.Label(content_frame, text="👤", font=("Arial", 30), 
                fg="#e74c3c", bg='#34495e').pack(pady=10)
        
        # Instruction message
        self.message_label = tk.Label(content_frame, text="Please, place your admin finger\non the sensor", 
                                     font=("Arial", 11), fg="#ecf0f1", bg='#34495e')
        self.message_label.pack(pady=5)
        
        # Status message
        self.status_label = tk.Label(content_frame, text="Waiting for admin fingerprint...", 
                                    font=("Arial", 9), fg="#95a5a6", bg='#34495e')
        self.status_label.pack(pady=5)
        
        # Cancel button
        self.cancel_btn = tk.Button(content_frame, text="Cancel", 
                                   font=("Arial", 9), bg="#e74c3c", fg="white",
                                   command=self.cancel_auth, cursor="hand2")
        self.cancel_btn.pack(pady=10)
    
    def update_status(self, message, color="#95a5a6"):
        """Update status message"""
        self.status_label.config(text=message, fg=color)
    
    def show_success(self):
        """Show success message"""
        self.update_status("✅ Admin authenticated!", "#27ae60")
        self.message_label.config(text="Welcome Admin!\nAccess Granted", fg="#27ae60")
        self.cancel_btn.config(text="Continue", bg="#27ae60")
        self.auth_result = True
        
        # Auto close after 2 seconds
        self.root.after(2000, self.close_window)
    
    def show_failed(self):
        """Show failed message"""
        self.update_status("❌ Authentication failed!", "#e74c3c")
        self.message_label.config(text="Authentication Failed\nAccess Denied", fg="#e74c3c")
        self.cancel_btn.config(text="Close", bg="#e74c3c")
        self.auth_result = False
        
        # Auto close after 3 seconds
        self.root.after(3000, self.close_window)
    
    def cancel_auth(self):
        """Cancel authentication"""
        self.auth_result = False
        self.close_window()
    
    def close_window(self):
        """Close the window"""
        try:
            self.root.destroy()
        except:
            pass

def authenticate_admin(max_attempts=3):
    """Authenticate admin using fingerprint with simple GUI"""
    print(f"\n🔐 ADMIN AUTHENTICATION")
    
    # Show GUI window
    try:
        admin_gui = AdminFingerprintGUI()
        
        # Start authentication in background
        def run_auth():
            attempts = 0
            
            while attempts < max_attempts:
                attempts += 1
                print(f"Admin attempt {attempts}/{max_attempts}")
                
                # Update GUI
                admin_gui.root.after(0, lambda: admin_gui.update_status(f"👆 Place admin finger... (Attempt {attempts}/{max_attempts})", "#3498db"))
                
                # Wait for finger and process
                finger_detected = False
                for _ in range(100):  # 10 second timeout
                    if finger.get_image() == adafruit_fingerprint.OK:
                        finger_detected = True
                        break
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
                
                if finger.image_2_tz(1) != adafruit_fingerprint.OK:
                    if attempts < max_attempts:
                        admin_gui.root.after(0, lambda: admin_gui.update_status("❌ Processing failed! Try again...", "#e74c3c"))
                        time.sleep(2)
                        continue
                    else:
                        admin_gui.root.after(0, admin_gui.show_failed)
                        return
                
                # Search for fingerprint
                admin_gui.root.after(0, lambda: admin_gui.update_status("🔍 Searching...", "#9b59b6"))
                
                if finger.finger_search() != adafruit_fingerprint.OK:
                    if attempts < max_attempts:
                        admin_gui.root.after(0, lambda: admin_gui.update_status("❌ No match found! Try again...", "#e74c3c"))
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
        # Fallback to console authentication
        return authenticate_admin_console(max_attempts)

def authenticate_admin_console(max_attempts=3):
    """Fallback console admin authentication"""
    attempts = 0
    
    while attempts < max_attempts:
        attempts += 1
        print(f"\n🔐 ADMIN AUTHENTICATION (Attempt {attempts}/{max_attempts})")
        print("👆 Place admin finger on sensor...")
        
        # Wait for finger and process
        while finger.get_image() != adafruit_fingerprint.OK:
            print(".", end="")
            time.sleep(0.1)
        
        print("\n🔄 Processing...")
        if finger.image_2_tz(1) != adafruit_fingerprint.OK:
            print("❌ Failed to process fingerprint")
            if attempts < max_attempts:
                print("🔄 Please try again...")
                time.sleep(1)
                continue
            else:
                print("❌ Maximum attempts reached. Authentication failed.")
                return False
        
        print("🔍 Searching...")
        if finger.finger_search() != adafruit_fingerprint.OK:
            print("❌ No match found")
            if attempts < max_attempts:
                print(f"🔄 Try again? ({max_attempts - attempts} attempts remaining)")
                choice = input("Press Enter to retry, or 'q' to quit: ").strip().lower()
                if choice == 'q':
                    print("❌ Admin authentication cancelled")
                    return False
                continue
            else:
                print("❌ Maximum attempts reached. Access denied.")
                return False
        
        # Check if matched fingerprint is admin (slot 1)
        if finger.finger_id == 1:
            try:
                admin_db = load_admin_database()
                admin_name = admin_db.get("1", {}).get("name", "Admin User")
            except:
                admin_name = "Admin User"
            
            print(f"✅ Welcome Admin: {admin_name}")
            print(f"🎯 Confidence: {finger.confidence}")
            return True
        else:
            print("❌ Not an admin fingerprint")
            if attempts < max_attempts:
                print(f"🔄 Please use admin fingerprint. Try again? ({max_attempts - attempts} attempts remaining)")
                choice = input("Press Enter to retry, or 'q' to quit: ").strip().lower()
                if choice == 'q':
                    print("❌ Admin authentication cancelled")
                    return False
                continue
            else:
                print("❌ Maximum attempts reached. Access denied.")
                return False
    
    return False# services/fingerprint.py - Complete Enhanced Fingerprint Service with GUI Authentication

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

# =================== DATABASE COMPATIBILITY FUNCTIONS ===================

def safe_get_student_by_id(student_id):
    """Safely get student by ID with fallback"""
    try:
        return get_student_by_id(student_id)
    except:
        # Fallback to get_user_by_id if specific function doesn't exist
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
        # Fallback to get_user_by_id if specific function doesn't exist
        try:
            result = get_user_by_id(staff_id)
            if result and result.get('user_type') == 'STAFF':
                return result
        except:
            pass
        return None

# =================== ENHANCED FINGERPRINT AUTHENTICATION GUI ===================

class FingerprintAuthGUI:
    """Enhanced Fingerprint Authentication GUI with attempt counter"""
    
    def __init__(self, max_attempts=5):
        self.max_attempts = max_attempts
        self.current_attempt = 0
        self.auth_result = None
        self.is_scanning = False
        
        # Create main window
        self.root = tk.Toplevel()
        self.root.title("Fingerprint Scanner")
        self.root.geometry("400x300")
        self.root.configure(bg='#2c3e50')
        self.root.resizable(False, False)
        
        # Center window
        self.center_window()
        
        # Make window stay on top
        self.root.transient()
        self.root.grab_set()
        
        # Create GUI elements
        self.create_widgets()
        
        # Start scanning process
        self.start_scanning()
    
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def create_widgets(self):
        """Create all GUI widgets"""
        # Title
        title_frame = tk.Frame(self.root, bg='#2c3e50')
        title_frame.pack(pady=20)
        
        tk.Label(title_frame, text="Fingerprint Scanner", 
                font=("Arial", 18, "bold"), fg="#ecf0f1", bg='#2c3e50').pack()
        
        # Main content frame
        content_frame = tk.Frame(self.root, bg='#34495e', relief='ridge', bd=2)
        content_frame.pack(padx=20, pady=10, fill='both', expand=True)
        
        # Fingerprint icon
        tk.Label(content_frame, text="👆", font=("Arial", 40), 
                fg="#3498db", bg='#34495e').pack(pady=10)
        
        # Instruction message
        self.message_label = tk.Label(content_frame, text="Please, place your finger\nin the sensor", 
                                     font=("Arial", 12), fg="#ecf0f1", bg='#34495e')
        self.message_label.pack(pady=5)
        
        # Attempt counter
        self.attempt_label = tk.Label(content_frame, text="Attempt 1/5", 
                                     font=("Arial", 11, "bold"), fg="#f39c12", bg='#34495e')
        self.attempt_label.pack(pady=5)
        
        # Status message
        self.status_label = tk.Label(content_frame, text="Scanning in progress...", 
                                    font=("Arial", 10), fg="#95a5a6", bg='#34495e')
        self.status_label.pack(pady=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(content_frame, mode='indeterminate', length=200)
        self.progress.pack(pady=10)
        self.progress.start()
        
        # Cancel button
        self.cancel_btn = tk.Button(content_frame, text="Cancel", 
                                   font=("Arial", 10), bg="#e74c3c", fg="white",
                                   command=self.cancel_auth, cursor="hand2")
        self.cancel_btn.pack(pady=10)
    
    def update_attempt_display(self):
        """Update the attempt counter display"""
        self.attempt_label.config(text=f"Attempt {self.current_attempt}/{self.max_attempts}")
        
        if self.current_attempt >= 3:
            self.attempt_label.config(fg="#e74c3c")  # Red for high attempts
        elif self.current_attempt >= 2:
            self.attempt_label.config(fg="#f39c12")  # Orange for medium attempts
    
    def update_status(self, message, color="#95a5a6"):
        """Update status message"""
        self.status_label.config(text=message, fg=color)
    
    def start_scanning(self):
        """Start the fingerprint scanning process"""
        if not self.is_scanning:
            self.is_scanning = True
            thread = threading.Thread(target=self.fingerprint_scan_loop, daemon=True)
            thread.start()
    
    def fingerprint_scan_loop(self):
        """Main fingerprint scanning loop"""
        while self.current_attempt < self.max_attempts and self.auth_result is None:
            self.current_attempt += 1
            
            # Update UI
            self.root.after(0, self.update_attempt_display)
            self.root.after(0, lambda: self.update_status("👆 Place finger on sensor...", "#3498db"))
            
            try:
                # Wait for finger placement (with timeout)
                finger_detected = self.wait_for_finger(timeout=10)
                
                if not finger_detected:
                    if self.current_attempt < self.max_attempts:
                        self.root.after(0, lambda: self.update_status("⏰ Timeout! Try again...", "#e67e22"))
                        time.sleep(2)
                        continue
                    else:
                        self.root.after(0, self.show_access_denied)
                        return
                
                # Process fingerprint
                self.root.after(0, lambda: self.update_status("🔄 Processing...", "#f39c12"))
                
                if finger.image_2_tz(1) != adafruit_fingerprint.OK:
                    if self.current_attempt < self.max_attempts:
                        self.root.after(0, lambda: self.update_status("❌ Processing failed! Try again...", "#e74c3c"))
                        time.sleep(2)
                        continue
                    else:
                        self.root.after(0, self.show_access_denied)
                        return
                
                # Search for match
                self.root.after(0, lambda: self.update_status("🔍 Searching...", "#9b59b6"))
                
                if finger.finger_search() != adafruit_fingerprint.OK:
                    if self.current_attempt < self.max_attempts:
                        self.root.after(0, lambda: self.update_status("❌ No match found! Try again...", "#e74c3c"))
                        time.sleep(2)
                        continue
                    else:
                        self.root.after(0, self.show_access_denied)
                        return
                
                # Success!
                self.root.after(0, self.show_success)
                return
                
            except Exception as e:
                print(f"❌ Fingerprint error: {e}")
                if self.current_attempt < self.max_attempts:
                    self.root.after(0, lambda: self.update_status("❌ Error! Try again...", "#e74c3c"))
                    time.sleep(2)
                    continue
                else:
                    self.root.after(0, self.show_access_denied)
                    return
        
        # If we get here, all attempts failed
        if self.auth_result is None:
            self.root.after(0, self.show_access_denied)
    
    def wait_for_finger(self, timeout=10):
        """Wait for finger placement with timeout"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if finger.get_image() == adafruit_fingerprint.OK:
                return True
            time.sleep(0.1)
        return False
    
    def show_success(self):
        """Show success message and get user info"""
        self.progress.stop()
        self.update_status("✅ Fingerprint verified!", "#27ae60")
        self.message_label.config(text="Authentication\nSuccessful!", fg="#27ae60")
        self.cancel_btn.config(text="Continue", bg="#27ae60")
        
        # Get user info
        try:
            # Load databases using available functions
            fingerprint_db = load_fingerprint_database()
            
            # Get fingerprint info
            finger_info = fingerprint_db.get(str(finger.finger_id), {})
            user_type = finger_info.get('user_type', 'UNKNOWN')
            
            # Get user details from database
            if user_type == 'STUDENT':
                user_id = finger_info.get('student_id', '')
                user_info = safe_get_student_by_id(user_id) or {}
            elif user_type == 'STAFF':
                user_id = finger_info.get('staff_no', '')
                user_info = safe_get_staff_by_id(user_id) or {}
            else:
                user_info = {}
            
            # Create standardized result
            self.auth_result = {
                "name": user_info.get('full_name', f"Unknown User (ID: {finger.finger_id})"),
                "student_id": finger_info.get('unified_id', user_id),
                "unified_id": finger_info.get('unified_id', user_id),
                "user_type": user_type,
                "course": user_info.get('course', user_info.get('staff_role', 'N/A')),
                "license_number": user_info.get('license_number', 'N/A'),
                "license_expiration": user_info.get('license_expiration', user_info.get('expiration_date', 'N/A')),
                "plate_number": user_info.get('plate_number', 'N/A'),
                "finger_id": finger.finger_id,
                "confidence": finger.confidence,
                "enrolled_date": user_info.get('enrolled_date', 'Unknown')
            }
            
        except Exception as e:
            print(f"❌ Error getting user info: {e}")
            self.auth_result = None
        
        # Auto close after 2 seconds
        self.root.after(2000, self.close_window)
    
    def show_access_denied(self):
        """Show access denied message"""
        self.progress.stop()
        self.update_status("❌ ACCESS DENIED", "#e74c3c")
        self.message_label.config(text="Maximum attempts\nreached!", fg="#e74c3c")
        self.attempt_label.config(text=f"Failed: {self.max_attempts}/{self.max_attempts}", fg="#e74c3c")
        self.cancel_btn.config(text="Close", bg="#e74c3c")
        
        self.auth_result = False
        
        # Auto close after 3 seconds
        self.root.after(3000, self.close_window)
    
    def cancel_auth(self):
        """Cancel authentication"""
        self.auth_result = False
        self.close_window()
    
    def close_window(self):
        """Close the window"""
        try:
            self.root.destroy()
        except:
            pass

# =================== MAIN AUTHENTICATION FUNCTIONS ===================

def authenticate_fingerprint(max_attempts=5):
    """
    Enhanced fingerprint authentication with GUI and attempt limiting
    
    Args:
        max_attempts (int): Maximum number of attempts allowed (default: 5)
    
    Returns:
        dict: User information if successful
        None: If authentication failed or was cancelled
    """
    print(f"\n🔒 Starting fingerprint authentication (Max attempts: {max_attempts})")
    
    try:
        # Create and show GUI
        auth_gui = FingerprintAuthGUI(max_attempts)
        
        # Wait for authentication to complete
        auth_gui.root.wait_window()
        
        # Return result
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

def authenticate_fingerprint_custom_retry(max_attempts=3):
    """Authenticate fingerprint with custom retry count"""
    return authenticate_fingerprint(max_attempts)

# =================== ADMIN AUTHENTICATION ===================

def authenticate_admin(max_attempts=3):
    """Authenticate admin using fingerprint with retry mechanism"""
    attempts = 0
    
    while attempts < max_attempts:
        attempts += 1
        print(f"\n🔐 ADMIN AUTHENTICATION (Attempt {attempts}/{max_attempts})")
        print("👆 Place admin finger on sensor...")
        
        # Wait for finger and process
        while finger.get_image() != adafruit_fingerprint.OK:
            print(".", end="")
            time.sleep(0.1)
        
        print("\n🔄 Processing...")
        if finger.image_2_tz(1) != adafruit_fingerprint.OK:
            print("❌ Failed to process fingerprint")
            if attempts < max_attempts:
                print("🔄 Please try again...")
                time.sleep(1)
                continue
            else:
                print("❌ Maximum attempts reached. Authentication failed.")
                return False
        
        print("🔍 Searching...")
        if finger.finger_search() != adafruit_fingerprint.OK:
            print("❌ No match found")
            if attempts < max_attempts:
                print(f"🔄 Try again? ({max_attempts - attempts} attempts remaining)")
                choice = input("Press Enter to retry, or 'q' to quit: ").strip().lower()
                if choice == 'q':
                    print("❌ Admin authentication cancelled")
                    return False
                continue
            else:
                print("❌ Maximum attempts reached. Access denied.")
                return False
        
        # Check if matched fingerprint is admin (slot 1)
        if finger.finger_id == 1:
            try:
                admin_db = load_admin_database()
                admin_name = admin_db.get("1", {}).get("name", "Admin User")
            except:
                admin_name = "Admin User"
            
            print(f"✅ Welcome Admin: {admin_name}")
            print(f"🎯 Confidence: {finger.confidence}")
            return True
        else:
            print("❌ Not an admin fingerprint")
            if attempts < max_attempts:
                print(f"🔄 Please use admin fingerprint. Try again? ({max_attempts - attempts} attempts remaining)")
                choice = input("Press Enter to retry, or 'q' to quit: ").strip().lower()
                if choice == 'q':
                    print("❌ Admin authentication cancelled")
                    return False
                continue
            else:
                print("❌ Maximum attempts reached. Access denied.")
                return False
    
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

def enroll_admin_fingerprint():
    """Enroll admin fingerprint in slot 1"""
    print(f"\n🔐 ADMIN FINGERPRINT ENROLLMENT")
    print("⚠️  This will enroll the admin fingerprint at slot #1")
    
    # Check if admin exists
    try:
        admin_db = load_admin_database()
        if "1" in admin_db:
            print(f"⚠️  Admin fingerprint already exists!")
            if input("Replace it? (y/N): ").lower() != 'y':
                print("❌ Cancelled.")
                return False
    except:
        pass
    
    # Get admin name
    admin_name = input("Enter admin name: ").strip()
    if not admin_name:
        print("❌ Admin name required.")
        return False
    
    # Enroll fingerprint at slot 1
    print(f"🔒 Enrolling admin fingerprint at slot #1")
    
    for fingerimg in range(1, 3):
        if fingerimg == 1:
            print("👆 Place finger on sensor for first scan...")
        else:
            print("👆 Place same finger again for second scan...")
        
        while finger.get_image() != adafruit_fingerprint.OK:
            pass
        
        print("🔄 Processing...", end="")
        if finger.image_2_tz(fingerimg) != adafruit_fingerprint.OK:
            print("❌ Failed")
            return False
        print("✅")
        
        if fingerimg == 1:
            print("🔄 Remove finger")
            time.sleep(1)
            while finger.get_image() == adafruit_fingerprint.OK:
                pass
    
    # Create template
    print("🔄 Creating template...", end="")
    if finger.create_model() != adafruit_fingerprint.OK:
        print("❌ Failed")
        return False
    print("✅")
    
    # Store at slot 1
    print("💾 Storing at slot #1...", end="")
    if finger.store_model(1) != adafruit_fingerprint.OK:
        print("❌ Failed")
        return False
    print("✅")
    
    # Save to database
    admin_db = load_admin_database()
    admin_db["1"] = {
        "name": admin_name,
        "enrolled_date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "slot": 1
    }
    save_admin_database(admin_db)
    
    print(f"✅ Admin fingerprint enrolled successfully!")
    print(f"👤 Admin: {admin_name}")
    print(f"🔒 Slot: #1")
    
    return True

# =================== USER ENROLLMENT FUNCTIONS ===================

def get_user_id_gui():
    """Get user ID via GUI and fetch info (works for both students and staff)"""
    root = tk.Tk()
    root.withdraw()
    
    while True:
        user_id = simpledialog.askstring("User Enrollment", 
                                        "Enter Student No. or Staff No.:")
        
        if not user_id:
            root.destroy()
            return None
        
        user_id = user_id.strip()
        user_info = get_user_by_id(user_id)  # This function now handles both types
        
        if user_info:
            # Determine display information based on user type
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
            else:  # STAFF
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

def show_message_gui(title, message):
    """Show message dialog"""
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo(title, message)
    root.destroy()

def display_user_info(user_info):
    """Display user info in console (works for both students and staff)"""
    print(f"\n{'='*50}")
    if user_info['user_type'] == 'STUDENT':
        print("📋 STUDENT INFORMATION")
        print(f"{'='*50}")
        print(f"👤 Name: {user_info['full_name']}")
        print(f"🆔 Student No.: {user_info['student_id']}")
        print(f"📚 Course: {user_info['course']}")
        print(f"🪪 License: {user_info['license_number']}")
        print(f"📅 Expiration: {user_info['expiration_date']}")
        print(f"🏍️ Plate: {user_info['plate_number']}")
    else:  # STAFF
        print("📋 STAFF INFORMATION")
        print(f"{'='*50}")
        print(f"👤 Name: {user_info['full_name']}")
        print(f"🆔 Staff No.: {user_info['staff_no']}")
        print(f"👔 Role: {user_info['staff_role']}")
        print(f"🪪 License: {user_info['license_number']}")
        print(f"📅 Expiration: {user_info['expiration_date']}")
        print(f"🏍️ Plate: {user_info['plate_number']}")
    print(f"{'='*50}")

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

def _capture_fingerprint_image(attempt_num, max_attempts=5):
    """Helper function to capture fingerprint image with retry logic"""
    print(f"👆 Place finger on sensor - Attempt {attempt_num}/{max_attempts}...")
    
    # Wait for finger with timeout
    finger_detected = False
    for _ in range(100):  # 10 second timeout
        if finger.get_image() == adafruit_fingerprint.OK:
            finger_detected = True
            break
        time.sleep(0.1)
        print(".", end="")
    
    if not finger_detected:
        print("\n⏰ Timeout waiting for finger")
        return False
    
    print("✅ Finger detected!")
    return True

def _process_fingerprint_template(template_num):
    """Helper function to process fingerprint template"""
    print("🔄 Processing...", end="")
    if finger.image_2_tz(template_num) != adafruit_fingerprint.OK:
        print("❌ Failed to process")
        return False
    print("✅")
    return True

def enroll_finger_with_user_info(location=None):
    """Enhanced enrollment using Student ID or Staff No with retry mechanism"""
    
    # Auto-find slot if not provided
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
    
    display_user_info(user_info)
    print(f"👤 Enrolling: {user_info['full_name']} ({user_info['user_type']})")
    
    # Fingerprint enrollment process with retry
    for fingerimg in range(1, 3):
        max_attempts = 5
        success = False
        
        for attempt in range(1, max_attempts + 1):
            if _capture_fingerprint_image(attempt, max_attempts):
                if _process_fingerprint_template(fingerimg):
                    success = True
                    break
            
            if attempt < max_attempts:
                retry = input("Try again? (y/N): ").lower() == 'y'
                if not retry:
                    print("❌ Enrollment cancelled")
                    return False
            else:
                print("❌ Maximum attempts reached")
                return False
        
        if not success:
            print("❌ Failed to capture fingerprint")
            return False
        
        if fingerimg == 1:
            print("🔄 Remove finger")
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
    else:  # STAFF
        database[str(location)].update({
            "staff_no": user_info['staff_no'],
            "unified_id": user_info['staff_no'],
            "staff_role": user_info['staff_role']
        })
    
    save_fingerprint_database(database)
    
    # Show success message
    if user_info['user_type'] == 'STUDENT':
        success_message = f"""
Enrollment Successful! ✅
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👤 Student: {user_info['full_name']}
🆔 Student No.: {user_info['student_id']}
📚 Course: {user_info['course']}
🪪 License: {user_info['license_number']}
🏍️ Plate: {user_info['plate_number']}
🔒 Fingerprint Slot: #{location}
📅 Enrolled: {time.strftime("%Y-%m-%d %H:%M:%S")}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
    else:  # STAFF
        success_message = f"""
Enrollment Successful! ✅
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👤 Staff: {user_info['full_name']}
🆔 Staff No.: {user_info['staff_no']}
👔 Role: {user_info['staff_role']}
🪪 License: {user_info['license_number']}
🏍️ Plate: {user_info['plate_number']}
🔒 Fingerprint Slot: #{location}
📅 Enrolled: {time.strftime("%Y-%m-%d %H:%M:%S")}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
    
    show_message_gui("Enrollment Complete", success_message)
    return True

# =================== FINGERPRINT MANAGEMENT FUNCTIONS ===================

def delete_fingerprint(finger_id):
    """Delete fingerprint from sensor and database"""
    try:
        # Delete from sensor
        if finger.delete_model(finger_id) != adafruit_fingerprint.OK:
            print(f"❌ Failed to delete fingerprint #{finger_id} from sensor")
            return False
        
        # Delete from database
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
        
        # Sort by slot number
        users.sort(key=lambda x: x['slot'])
        return users
        
    except Exception as e:
        print(f"❌ Error getting enrolled users: {e}")
        return []

def view_enrolled_users():
    """Display all enrolled users in a formatted table"""
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

def clear_all_fingerprints():
    """Clear all fingerprints except admin (dangerous operation)"""
    try:
        # Get enrolled users first
        users = get_enrolled_users()
        
        if not users:
            print("📝 No fingerprints to clear")
            return True
        
        print(f"⚠️ This will delete {len(users)} fingerprints (admin excluded)")
        
        # Delete each fingerprint
        for user in users:
            if delete_fingerprint(user['slot']):
                print(f"🗑️ Deleted: {user['name']} (slot #{user['slot']})")
            else:
                print(f"❌ Failed to delete: {user['name']} (slot #{user['slot']})")
        
        print("✅ Fingerprint clearing completed")
        return True
        
    except Exception as e:
        print(f"❌ Error clearing fingerprints: {e}")
        return False

# =================== SENSOR UTILITY FUNCTIONS ===================

def get_sensor_info():
    """Get fingerprint sensor information"""
    try:
        print("\n🔍 FINGERPRINT SENSOR INFO")
        print("=" * 40)
        print(f"📊 Library size: {finger.library_size}")
        print(f"🔧 Template count: {finger.template_count}")
        print(f"📡 Security level: {finger.security_level}")
        print(f"📱 Baud rate: {finger.baud_rate}")
        print("=" * 40)
        
        return {
            'library_size': finger.library_size,
            'template_count': finger.template_count,
            'security_level': finger.security_level,
            'baud_rate': finger.baud_rate
        }
    except Exception as e:
        print(f"❌ Error getting sensor info: {e}")
        return None

def test_sensor_connection():
    """Test fingerprint sensor connection"""
    try:
        print("\n🔍 Testing sensor connection...")
        
        # Try to read sensor info
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

# =================== BACKUP AND RESTORE FUNCTIONS ===================

def backup_fingerprint_database(backup_path=None):
    """Backup fingerprint database to file"""
    try:
        if backup_path is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            backup_path = f"backups/fingerprint_backup_{timestamp}.json"
        
        # Create backup directory
        os.makedirs(os.path.dirname(backup_path), exist_ok=True)
        
        # Load current database
        database = load_fingerprint_database()
        
        # Add metadata
        backup_data = {
            "backup_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_users": len([k for k in database.keys() if k != "1"]),  # Exclude admin
            "database": database
        }
        
        # Save backup
        with open(backup_path, 'w') as f:
            json.dump(backup_data, f, indent=4)
        
        print(f"✅ Database backed up to: {backup_path}")
        return backup_path
        
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        return None

def restore_fingerprint_database(backup_path):
    """Restore fingerprint database from backup file"""
    try:
        if not os.path.exists(backup_path):
            print(f"❌ Backup file not found: {backup_path}")
            return False
        
        # Load backup
        with open(backup_path, 'r') as f:
            backup_data = json.load(f)
        
        # Validate backup structure
        if "database" not in backup_data:
            print("❌ Invalid backup file format")
            return False
        
        # Restore database
        save_fingerprint_database(backup_data["database"])
        
        backup_date = backup_data.get("backup_date", "Unknown")
        total_users = backup_data.get("total_users", 0)
        
        print(f"✅ Database restored from backup")
        print(f"📅 Backup date: {backup_date}")
        print(f"👥 Users restored: {total_users}")
        
        return True
        
    except Exception as e:
        print(f"❌ Restore failed: {e}")
        return False

# =================== LEGACY SUPPORT FUNCTIONS ===================

def enroll_finger_with_name(location):
    """Legacy function - redirects to new enrollment"""
    return enroll_finger_with_user_info(location)

def authenticate_fingerprint_simple():
    """Simple authentication without GUI (for backwards compatibility)"""
    print("\n🔒 Simple Fingerprint Authentication")
    print("👆 Place finger on sensor...")
    
    # Wait for finger
    while finger.get_image() != adafruit_fingerprint.OK:
        pass
    
    # Process and search
    if finger.image_2_tz(1) != adafruit_fingerprint.OK:
        print("❌ Processing failed")
        return None
    
    if finger.finger_search() != adafruit_fingerprint.OK:
        print("❌ No match found")
        return None
    
    # Get user info
    database = load_fingerprint_database()
    finger_info = database.get(str(finger.finger_id), {})
    
    print(f"✅ Authenticated: {finger_info.get('name', 'Unknown')}")
    return finger_info

# =================== VIP FUNCTIONS ===================

def authenticate_admin_for_vip():
    """Special admin authentication for VIP access"""
    print("\n🔐 VIP ACCESS - Admin Authentication Required")
    return authenticate_admin(max_attempts=3)

# =================== TESTING AND DEBUG FUNCTIONS ===================

def debug_fingerprint_sensor():
    """Debug function to test all sensor functions"""
    print("\n🔬 FINGERPRINT SENSOR DEBUG")
    print("=" * 50)
    
    # Test connection
    print("1️⃣ Testing connection...")
    if test_sensor_connection():
        print("   ✅ Connection OK")
    else:
        print("   ❌ Connection failed")
        return
    
    # Get sensor info
    print("\n2️⃣ Getting sensor info...")
    sensor_info = get_sensor_info()
    if sensor_info:
        print("   ✅ Sensor info retrieved")
    else:
        print("   ❌ Failed to get sensor info")
    
    # Check enrolled users
    print("\n3️⃣ Checking enrolled users...")
    users = get_enrolled_users()
    print(f"   📊 {len(users)} users enrolled")
    
    # Check admin
    print("\n4️⃣ Checking admin fingerprint...")
    if check_admin_fingerprint_exists():
        print("   ✅ Admin fingerprint exists")
    else:
        print("   ⚠️ Admin fingerprint not found")
    
    print("\n🏁 Debug completed")

# =================== INITIALIZATION ===================

def init_fingerprint_service():
    """Initialize fingerprint service and check sensor"""
    print("🔧 Initializing fingerprint service...")
    
    try:
        # Test sensor connection
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

# =================== MAIN FUNCTION FOR TESTING ===================

if __name__ == "__main__":
    """Test the fingerprint service"""
    print("🚀 FINGERPRINT SERVICE TEST")
    
    # Initialize
    if not init_fingerprint_service():
        print("❌ Service initialization failed")
        exit(1)
    
    # Debug sensor
    debug_fingerprint_sensor()
    
    # Test authentication
    print("\n🔒 Testing authentication...")
    result = authenticate_fingerprint(max_attempts=3)
    
    if result:
        print(f"✅ Test successful: {result['name']}")
    else:
        print("❌ Test failed")
    
    print("\n🏁 Test completed")
