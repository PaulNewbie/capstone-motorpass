# fingerprint_gui.py - GUI Components for Fingerprint Service

import tkinter as tk
from tkinter import messagebox, ttk
import threading
import time

from etc.services.hardware.fingerprint import finger, load_fingerprint_database, safe_get_student_by_id, safe_get_staff_by_id
import adafruit_fingerprint

# For ADMIN GUI Fingerprint
class AdminFingerprintGUI:
    def __init__(self, parent_window=None):
        self.auth_result = False
        self.parent_window = parent_window
        
        # Create main window
        self.root = tk.Toplevel(parent_window)
        self.root.title("Admin Authentication")
        self.root.geometry("350x250")
        self.root.configure(bg='#2c3e50')
        self.root.resizable(False, False)
        
        # Use overrideredirect to prevent window manager interference
        self.root.overrideredirect(True)
        
        # Keep parent window visible and ensure stacking order
        if parent_window:
            parent_window.attributes('-topmost', False)  # Remove topmost if set
            parent_window.deiconify()  # Ensure parent is visible
            parent_window.update()     # Force update
        
        # Center window PROPERLY - fix the positioning issue
        self.center_window()
        
        # Set this window on top but not topmost
        self.root.lift()
        self.root.focus_force()
        
        # Create GUI elements
        self.create_widgets()
    
    def center_window(self):
        """Center the window on screen - FIXED"""
        # First update to get correct dimensions
        self.root.update_idletasks()
        
        # Get window dimensions
        width = 350  # Use fixed width since geometry is set
        height = 250  # Use fixed height since geometry is set
        
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Calculate center position
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        
        # Set the geometry with proper positioning
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
        # Force update to apply positioning
        self.root.update()
    
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
        """Show success message - NEVER hides main window"""
        self.update_status("✅ Admin authenticated!", "#27ae60")
        self.message_label.config(text="Welcome Admin!\nAccess Granted", fg="#27ae60")
        self.cancel_btn.config(text="Continue", bg="#27ae60")
        self.auth_result = True
        
        # IMPORTANT: Keep main window visible during success
        if self.parent_window:
            self.parent_window.deiconify()  # Ensure main window stays visible
            self.parent_window.lift()       # Bring it to front
        
        # Close authentication window after 2 seconds
        # Main window hiding will be handled by the calling controller
        self.root.after(2000, self.close_window)
    
    def show_failed(self):
        """Show failed message - keep main window visible"""
        self.update_status("❌ Authentication failed!", "#e74c3c")
        self.message_label.config(text="Authentication Failed\nAccess Denied", fg="#e74c3c")
        self.cancel_btn.config(text="Close", bg="#e74c3c")
        self.auth_result = False
        
        # Ensure main window stays visible on failure
        if self.parent_window:
            self.parent_window.deiconify()
            self.parent_window.lift()
        
        # Auto close after 3 seconds
        self.root.after(3000, self.close_window)
    
    def cancel_auth(self):
        """Cancel authentication - keep main window visible"""
        self.auth_result = False
        
        # Ensure main window stays visible when cancelled
        if self.parent_window:
            self.parent_window.deiconify()
            self.parent_window.lift()
        
        self.close_window()
    
    def close_window(self):
        """Close the authentication window - NEVER hides main window"""
        try:
            # IMPORTANT: Main window visibility is controlled by calling code
            # This GUI class only handles authentication, not window management
            self.root.destroy()
        except:
            pass
                     
# For Student/Staff GUI Fingerprint
class FingerprintAuthGUI:
    """Enhanced Fingerprint Authentication GUI for students/staff"""
    
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
            fingerprint_db = load_fingerprint_database()
            finger_info = fingerprint_db.get(str(finger.finger_id), {})
            user_type = finger_info.get('user_type', 'UNKNOWN')
            
            # Initialize user_id to avoid UnboundLocalError
            user_id = ''
            
            # Get user details from database
            if user_type == 'STUDENT':
                user_id = finger_info.get('student_id', '')
                user_info = safe_get_student_by_id(user_id) or {}
            elif user_type == 'STAFF':
                user_id = finger_info.get('staff_no', '')
                user_info = safe_get_staff_by_id(user_id) or {}
            else:
                # For unknown user types, try to get unified_id as fallback
                user_id = finger_info.get('unified_id', '')
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
            
# Helper function to create GUI instances
def create_admin_auth_gui(parent_window=None):
    """Create and return AdminFingerprintGUI instance"""
    return AdminFingerprintGUI(parent_window)

def create_fingerprint_auth_gui(max_attempts=5):
    """Create and return FingerprintAuthGUI instance"""
    return FingerprintAuthGUI(max_attempts)
