# etc/ui/enrollment_fingerprint_gui.py
import tkinter as tk
from tkinter import ttk
import threading
import time

class EnrollmentFingerprintGUI:
    """Simple GUI for fingerprint enrollment - requires 2 scans"""
    
    def __init__(self, parent_window=None, user_name="User"):
        self.parent_window = parent_window
        self.user_name = user_name
        self.enrollment_result = None
        self.current_scan = 1  # Track which scan we're on (1 or 2)
        
        # Create enrollment window
        self.root = tk.Toplevel() if parent_window else tk.Tk()
        self.root.title("Fingerprint Enrollment")
        self.root.geometry("400x350")
        self.root.configure(bg='#2c3e50')
        self.root.resizable(False, False)
        
        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.root.winfo_screenheight() // 2) - (350 // 2)
        self.root.geometry(f"400x350+{x}+{y}")
        
        # Keep on top
        self.root.attributes('-topmost', True)
        
        self.create_widgets()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.cancel_enrollment)
    
    def create_widgets(self):
        """Create GUI elements"""
        # Main frame with border
        main_frame = tk.Frame(self.root, bg='#34495e', relief='ridge', bd=2)
        main_frame.pack(padx=15, pady=15, fill='both', expand=True)
        
        # Title
        tk.Label(main_frame, text="Fingerprint Enrollment", 
                font=("Arial", 14, "bold"), fg="#ecf0f1", bg='#34495e').pack(pady=10)
        
        # User info
        tk.Label(main_frame, text=f"Enrolling: {self.user_name}", 
                font=("Arial", 10), fg="#bdc3c7", bg='#34495e').pack(pady=5)
        
        # Fingerprint icon
        tk.Label(main_frame, text="👆", font=("Arial", 40), 
                fg="#3498db", bg='#34495e').pack(pady=10)
        
        # Scan indicator
        self.scan_label = tk.Label(main_frame, text="Scan 1 of 2", 
                                   font=("Arial", 12, "bold"), fg="#f39c12", bg='#34495e')
        self.scan_label.pack(pady=5)
        
        # Instruction message
        self.message_label = tk.Label(main_frame, text="Please place your finger\non the sensor", 
                                     font=("Arial", 11), fg="#ecf0f1", bg='#34495e')
        self.message_label.pack(pady=5)
        
        # Status message
        self.status_label = tk.Label(main_frame, text="Waiting for fingerprint...", 
                                    font=("Arial", 9), fg="#95a5a6", bg='#34495e')
        self.status_label.pack(pady=10)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate', length=250)
        self.progress.pack(pady=10)
        self.progress.start(10)
        
        # Cancel button
        self.cancel_btn = tk.Button(main_frame, text="Cancel", 
                                   font=("Arial", 9), bg="#e74c3c", fg="white",
                                   command=self.cancel_enrollment, cursor="hand2",
                                   padx=20, pady=5)
        self.cancel_btn.pack(pady=10)
    
    def update_status(self, message, color="#95a5a6"):
        """Update status message"""
        self.status_label.config(text=message, fg=color)
    
    def update_scan_number(self, scan_num):
        """Update which scan we're on"""
        self.current_scan = scan_num
        self.scan_label.config(text=f"Scan {scan_num} of 2")
        
        if scan_num == 2:
            self.message_label.config(text="Place the SAME finger again\nfor verification")
    
    def show_remove_finger(self):
        """Show message to remove finger"""
        self.update_status("✋ Remove finger...", "#e67e22")
        self.message_label.config(text="Please remove your finger\nand wait...", fg="#e67e22")
    
    def show_success(self):
        """Show success message"""
        self.progress.stop()
        self.update_status("✅ Enrollment successful!", "#27ae60")
        self.message_label.config(text="Fingerprint enrolled\nsuccessfully!", fg="#27ae60")
        self.scan_label.config(text="Complete!", fg="#27ae60")
        self.cancel_btn.config(text="Done", bg="#27ae60")
        self.enrollment_result = True
        
        # Close after 2 seconds
        self.root.after(2000, self.close_window)
    
    def show_failed(self):
        """Show failed message"""
        self.progress.stop()
        self.update_status("❌ Enrollment failed!", "#e74c3c")
        self.message_label.config(text="Failed to enroll fingerprint\nPlease try again", fg="#e74c3c")
        self.cancel_btn.config(text="Close", bg="#e74c3c")
        self.enrollment_result = False
        
        # Close after 3 seconds
        self.root.after(3000, self.close_window)
    
    def cancel_enrollment(self):
        """Cancel enrollment"""
        self.enrollment_result = False
        self.close_window()
    
    def close_window(self):
        """Close the window"""
        try:
            self.root.quit()
            self.root.destroy()
        except:
            pass
    
    def wait_for_result(self):
        """Wait for enrollment to complete"""
        self.root.mainloop()
        return self.enrollment_result


# Example usage in admin_enroll():
"""
def admin_enroll():
    '''Enroll new user with GUI'''
    from etc.ui.enrollment_fingerprint_gui import EnrollmentFingerprintGUI
    from etc.services.hardware.fingerprint import finger
    import adafruit_fingerprint
    
    # Get user info first
    user_info = get_user_id_gui()
    if not user_info:
        return
    
    # Find slot
    location = find_next_available_slot()
    
    # Create GUI
    enroll_gui = EnrollmentFingerprintGUI(user_name=user_info['full_name'])
    
    def run_enrollment():
        try:
            # Scan 1
            enroll_gui.root.after(0, lambda: enroll_gui.update_scan_number(1))
            enroll_gui.root.after(0, lambda: enroll_gui.update_status("👆 Place finger...", "#3498db"))
            
            # Wait for finger
            while finger.get_image() != adafruit_fingerprint.OK:
                time.sleep(0.1)
            
            enroll_gui.root.after(0, lambda: enroll_gui.update_status("🔄 Processing...", "#f39c12"))
            
            if finger.image_2_tz(1) != adafruit_fingerprint.OK:
                enroll_gui.root.after(0, enroll_gui.show_failed)
                return
            
            # Remove finger
            enroll_gui.root.after(0, enroll_gui.show_remove_finger)
            time.sleep(2)
            while finger.get_image() == adafruit_fingerprint.OK:
                time.sleep(0.1)
            
            # Scan 2
            enroll_gui.root.after(0, lambda: enroll_gui.update_scan_number(2))
            enroll_gui.root.after(0, lambda: enroll_gui.update_status("👆 Place same finger again...", "#3498db"))
            
            # Wait for finger again
            while finger.get_image() != adafruit_fingerprint.OK:
                time.sleep(0.1)
            
            enroll_gui.root.after(0, lambda: enroll_gui.update_status("🔄 Processing...", "#f39c12"))
            
            if finger.image_2_tz(2) != adafruit_fingerprint.OK:
                enroll_gui.root.after(0, enroll_gui.show_failed)
                return
            
            # Create model
            enroll_gui.root.after(0, lambda: enroll_gui.update_status("🔄 Creating template...", "#9b59b6"))
            
            if finger.create_model() != adafruit_fingerprint.OK:
                enroll_gui.root.after(0, enroll_gui.show_failed)
                return
            
            # Store model
            enroll_gui.root.after(0, lambda: enroll_gui.update_status("💾 Saving...", "#9b59b6"))
            
            if finger.store_model(location) != adafruit_fingerprint.OK:
                enroll_gui.root.after(0, enroll_gui.show_failed)
                return
            
            # Success - save to database
            database = load_fingerprint_database()
            database[str(location)] = {
                "name": user_info['full_name'],
                "user_type": user_info['user_type'],
                # ... rest of user info
            }
            save_fingerprint_database(database)
            
            enroll_gui.root.after(0, enroll_gui.show_success)
            
        except Exception as e:
            print(f"Enrollment error: {e}")
            enroll_gui.root.after(0, enroll_gui.show_failed)
    
    # Start enrollment in thread
    threading.Thread(target=run_enrollment, daemon=True).start()
    
    # Wait for result
    return enroll_gui.wait_for_result()
"""
