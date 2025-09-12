# etc/controllers/auth/fingerprint_vip.py
# VIP-specific fingerprint authentication that doesn't hide main window

import time
import serial
import adafruit_fingerprint
import threading
import tkinter as tk

# =================== HARDWARE SETUP ===================
uart = serial.Serial("/dev/ttyS0", baudrate=57600, timeout=1)
finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)

# =================== VIP-SPECIFIC GUI CLASS ===================

class VIPFingerprintGUI:
    """Fingerprint GUI specifically for VIP access - doesn't hide main window"""
    
    def __init__(self, parent_window=None):
        self.auth_result = False
        self.parent_window = parent_window
        
        # Create main window
        self.root = tk.Toplevel(parent_window)
        self.root.title("VIP Authentication!!!!!")
        self.root.geometry("350x250")
        self.root.configure(bg='#2c3e50')
        self.root.resizable(False, False)
        
        # Use overrideredirect to prevent window manager interference
        self.root.overrideredirect(True)
        
        # Keep parent window visible
        if parent_window:
            parent_window.attributes('-topmost', False)
            parent_window.deiconify()
            parent_window.update()
        
        # Center window
        self.center_window()
        
        # Set this window on top
        self.root.lift()
        self.root.focus_force()
        
        # Create GUI elements
        self.create_widgets()
    
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        
        width = 350
        height = 250
        
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        self.root.update()
    
    def create_widgets(self):
        """Create VIP authentication widgets"""
        # Title
        title_frame = tk.Frame(self.root, bg='#2c3e50')
        title_frame.pack(pady=15)
        
        tk.Label(title_frame, text="🌟 VIP Authentication", 
                font=("Arial", 16, "bold"), fg="#FF4444", bg='#2c3e50').pack()
        
        # Main content frame
        content_frame = tk.Frame(self.root, bg='#34495e', relief='ridge', bd=2)
        content_frame.pack(padx=20, pady=10, fill='both', expand=True)
        
        # VIP icon
        tk.Label(content_frame, text="👑", font=("Arial", 30), 
                fg="#FF4444", bg='#34495e').pack(pady=10)
        
        # Instruction message
        self.message_label = tk.Label(content_frame, text="Please place admin finger\nfor VIP access", 
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
        """Show success message - VIP VERSION (doesn't hide main window)"""
        self.update_status("✅ VIP access granted!", "#27ae60")
        self.message_label.config(text="VIP Access Granted!\nOpening panel...", fg="#27ae60")
        self.cancel_btn.config(text="Continue", bg="#27ae60")
        self.auth_result = True
        
        # Close after 2 seconds WITHOUT hiding main window
        self.root.after(2000, self.close_window)
    
    def show_failed(self):
        """Show failed message - keep main window visible"""
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
        """Close the authentication window - VIP VERSION"""
        try:
            # IMPORTANT: Don't hide parent window for VIP access
            self.root.destroy()
        except:
            pass

# =================== VIP AUTHENTICATION FUNCTION ===================

def authenticate_admin(max_attempts=3, parent_window=None):
    """Authenticate admin for VIP access - doesn't hide main window"""
    print(f"\n🌟 VIP ADMIN AUTHENTICATION!!!!!!!")
    
    try:
        vip_gui = VIPFingerprintGUI(parent_window=parent_window)
        
        def run_auth():
            attempts = 0
            
            while attempts < max_attempts:
                attempts += 1
                print(f"VIP attempt {attempts}/{max_attempts}")
                
                vip_gui.root.after(0, lambda: vip_gui.update_status(f"👆 Place admin finger... (Attempt {attempts}/{max_attempts})", "#3498db"))
                
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
                        vip_gui.root.after(0, lambda: vip_gui.update_status("⏰ Timeout! Try again...", "#e67e22"))
                        time.sleep(2)
                        continue
                    else:
                        vip_gui.root.after(0, vip_gui.show_failed)
                        return
                
                # Process fingerprint
                vip_gui.root.after(0, lambda: vip_gui.update_status("🔄 Processing...", "#f39c12"))
                
                try:
                    if finger.image_2_tz(1) != adafruit_fingerprint.OK:
                        if attempts < max_attempts:
                            vip_gui.root.after(0, lambda: vip_gui.update_status("❌ Processing failed! Try again...", "#e74c3c"))
                            time.sleep(2)
                            continue
                        else:
                            vip_gui.root.after(0, vip_gui.show_failed)
                            return
                except:
                    if attempts < max_attempts:
                        vip_gui.root.after(0, lambda: vip_gui.update_status("❌ Sensor error! Try again...", "#e74c3c"))
                        time.sleep(2)
                        continue
                    else:
                        vip_gui.root.after(0, vip_gui.show_failed)
                        return
                
                # Search for fingerprint
                vip_gui.root.after(0, lambda: vip_gui.update_status("🔍 Searching...", "#9b59b6"))
                
                try:
                    if finger.finger_search() != adafruit_fingerprint.OK:
                        if attempts < max_attempts:
                            vip_gui.root.after(0, lambda: vip_gui.update_status("❌ No match found! Try again...", "#e74c3c"))
                            time.sleep(2)
                            continue
                        else:
                            vip_gui.root.after(0, vip_gui.show_failed)
                            return
                    
                    # Check if matched fingerprint is admin (slot 1)
                    if finger.finger_id == 1:
                        vip_gui.root.after(0, vip_gui.show_success)
                        return
                    else:
                        if attempts < max_attempts:
                            vip_gui.root.after(0, lambda: vip_gui.update_status("❌ Not admin fingerprint! Try again...", "#e74c3c"))
                            time.sleep(2)
                            continue
                        else:
                            vip_gui.root.after(0, vip_gui.show_failed)
                            return
                            
                except:
                    if attempts < max_attempts:
                        vip_gui.root.after(0, lambda: vip_gui.update_status("❌ Search failed! Try again...", "#e74c3c"))
                        time.sleep(2)
                        continue
                    else:
                        vip_gui.root.after(0, vip_gui.show_failed)
                        return
            
            # All attempts failed
            vip_gui.root.after(0, vip_gui.show_failed)
        
        # Start authentication in thread
        auth_thread = threading.Thread(target=run_auth, daemon=True)
        auth_thread.start()
        
        # Wait for GUI to close
        vip_gui.root.wait_window()
        
        # Return result
        result = vip_gui.auth_result
        if result:
            print("✅ VIP Admin authentication successful!")
        else:
            print("❌ VIP Admin authentication failed!")
        
        return result
        
    except Exception as e:
        print(f"❌ VIP Admin authentication error: {e}")
        return False

