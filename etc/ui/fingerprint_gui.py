# fingerprint_gui.py - GUI Components for Fingerprint Service

import tkinter as tk
from tkinter import messagebox, ttk
import threading
import time


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

# Helper function to create GUI instances
def create_admin_auth_gui(parent_window=None):
    """Create and return AdminFingerprintGUI instance"""
    return AdminFingerprintGUI(parent_window)

def create_fingerprint_auth_gui(max_attempts=5):
    """Create and return FingerprintAuthGUI instance"""
    return FingerprintAuthGUI(max_attempts)
