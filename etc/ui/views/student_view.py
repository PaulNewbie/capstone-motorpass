# ui/views/student_view.py - ACTUALLY using reusable components, no duplication

import tkinter as tk
import threading
from datetime import datetime

# Import EXISTING reusable components - no duplication
from ui.components.window_helpers import WindowManager, ResponsiveCalculator
from ui.components.verification_components import VerificationUIComponents
from ui.business.student_operations import StudentVerificationManager

# Import refresh safely
try:
    import sys
    import os
    parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    from refresh import add_refresh_to_window
except ImportError:
    def add_refresh_to_window(window):
        try:
            window.bind('<F5>', lambda e: print("F5 refresh requested"))
        except:
            pass


class StudentVerificationView:
    """Student verification GUI using ACTUAL reusable components"""
    
    def __init__(self, verification_function):
        self.root = tk.Tk()
        self.verification_function = verification_function
        self.verification_complete = False
        
        # Use EXISTING WindowManager - no duplication
        self.screen_info = WindowManager.setup_fullscreen_window(
            root=self.root,
            title="MotorPass - Student/Staff Verification",
            bg_color='#8B4513'
        )
        
        # Use EXISTING ResponsiveCalculator - no duplication
        self.font_sizes = ResponsiveCalculator.calculate_font_sizes(self.screen_info['display_size'])
        self.padding_sizes = ResponsiveCalculator.calculate_padding_sizes(
            self.screen_info['screen_width'], self.screen_info['screen_height']
        )
        
        # Initialize business logic manager - actual separation
        self.verification_manager = StudentVerificationManager()
        
        if add_refresh_to_window:
            add_refresh_to_window(self.root)
            
        self.create_variables()
        self.create_interface()
        
        # Bind keys
        self.root.bind('<Escape>', lambda e: self.close())
        self.root.bind('<F11>', self.toggle_fullscreen)
        
    def toggle_fullscreen(self, event=None):
        """Toggle fullscreen"""
        try:
            current_state = self.root.attributes('-fullscreen')
            self.root.attributes('-fullscreen', not current_state)
        except Exception as e:
            print(f"Error toggling fullscreen: {e}")
        
    def create_variables(self):
        """Create tkinter variables"""
        self.helmet_status = tk.StringVar(value="PENDING")
        self.fingerprint_status = tk.StringVar(value="PENDING") 
        self.license_status = tk.StringVar(value="PENDING")
        self.current_step = tk.StringVar(value="Starting verification process...")
        self.time_string = tk.StringVar()
        self.date_string = tk.StringVar()
        self.update_time()
        
    def update_time(self):
        """Update time display"""
        try:
            if not hasattr(self, 'root') or not self.root.winfo_exists():
                return
                
            now = datetime.now()
            self.time_string.set(now.strftime("%H:%M:%S"))
            self.date_string.set(now.strftime("%A, %B %d, %Y"))
            
            if not self.verification_complete and self.root.winfo_exists():
                self._update_timer = self.root.after(1000, self.update_time)
        except (tk.TclError, Exception):
            pass
    
    def create_interface(self):
        """Create interface using ACTUAL reusable components"""
        # Main container
        main_container = tk.Frame(self.root, bg='#8B4513')
        main_container.pack(fill="both", expand=True)
        
        # Header - USE reusable component
        VerificationUIComponents.create_motorpass_header(
            parent=main_container,
            screen_info=self.screen_info,
            time_string=self.time_string,
            date_string=self.date_string,
            subtitle="Student & Staff Verification System"
        )
        
        # Content area
        content_frame = tk.Frame(main_container, bg='#8B4513')
        content_frame.pack(fill="both", expand=True, 
                          padx=self.padding_sizes['content_x'], 
                          pady=self.padding_sizes['content_y'])
        
        # Title
        title_font_size = max(24, int(min(self.screen_info['screen_width'], self.screen_info['screen_height']) / 32))
        title_label = tk.Label(content_frame, text="STUDENT/STAFF VERIFICATION", 
                              font=("Arial", title_font_size, "bold"), fg="#FFFFFF", bg='#8B4513')
        title_label.pack(pady=(0, self.padding_sizes['section_spacing']))
        
        # Main panels
        panels_container = tk.Frame(content_frame, bg='#8B4513')
        panels_container.pack(fill="both", expand=True)
        
        # Left panel - USE reusable status panel component
        self.create_status_panel(panels_container)
        
        # Right panel - USE reusable camera component
        right_frame = tk.Frame(panels_container, bg='#8B4513')
        right_frame.pack(side="right", fill="both", expand=True)
        
        VerificationUIComponents.create_camera_feed_panel(
            parent=right_frame,
            screen_info=self.screen_info
        )
        
        # Footer - USE reusable component
        VerificationUIComponents.create_verification_footer(
            parent=main_container,
            screen_info=self.screen_info,
            footer_text="Helmet Check → Fingerprint Scan → License Verification | ESC to exit"
        )
        
    def create_status_panel(self, parent):
        """Create status panel using reusable components"""
        left_frame = tk.Frame(parent, bg='#8B4513')
        left_frame.pack(side="left", fill="both", expand=True, 
                       padx=(0, self.padding_sizes['section_spacing']))
        
        # Define status variables for reusable component
        status_vars = {
            'helmet': ("🪖 HELMET CHECK:", self.helmet_status),
            'fingerprint': ("👆 FINGERPRINT:", self.fingerprint_status),
            'license': ("🪪 LICENSE CHECK:", self.license_status)
        }
        
        # USE reusable status panel component
        status_panel = VerificationUIComponents.create_status_panel(
            parent=left_frame,
            status_vars=status_vars,
            screen_info=self.screen_info,
            title="VERIFICATION STATUS"
        )
        
        # Add user info panel using reusable component
        user_info_components = VerificationUIComponents.create_user_info_panel(
            parent=status_panel['container'],
            screen_info=self.screen_info
        )
        
        # Store references for later use
        self.user_info_panel = user_info_components['panel']
        self.user_details_frame = user_info_components['details_frame']

    def show_user_info(self, user_info):
        """Display user info using reusable component"""
        # Define fields specific to student verification
        student_fields = [
            ("Name:", 'name'),
            ("Student ID:", 'student_id'),
            ("Course:", 'course'),
            ("User Type:", 'user_type')
        ]
        
        # USE reusable component
        VerificationUIComponents.update_user_info_display(
            user_details_frame=self.user_details_frame,
            user_info=user_info,
            screen_info=self.screen_info,
            info_fields=student_fields
        )
        
        # Show the panel
        panel_spacing_y = max(15, int(self.screen_info['screen_height'] * 0.02))
        self.user_info_panel.pack(fill="x", pady=(panel_spacing_y, 0))

    def update_status(self, status_dict):
        """Update status using business logic manager"""
        self.verification_manager.update_status(status_dict, self)
        
    def start_verification(self):
        """Start verification using business logic manager"""
        self.verification_manager.start_verification(self.verification_function, self.update_status_callback)

    def update_status_callback(self, status_dict):
        """Callback for status updates"""
        try:
            self.root.after(0, lambda: self.update_status(status_dict))
        except Exception as e:
            print(f"Error in callback: {e}")

    def close(self):
        """Close the GUI"""
        try:
            self.verification_complete = True
            if hasattr(self, '_update_timer'):
                self.root.after_cancel(self._update_timer)
            self.root.quit()
            self.root.destroy()
        except Exception as e:
            print(f"Error closing GUI: {e}")

    def run(self):
        """Run the GUI"""
        try:
            print(f"\n{'='*60}")
            print(f"🎓 Student Verification GUI Started")
            print(f"📱 Responsive Mode: {self.screen_info['screen_width']}x{self.screen_info['screen_height']}")
            if self.screen_info['is_square_display']:
                print(f"📺 Display Type: Square/4:3 Touch Screen Optimized")
            print(f"{'='*60}")
            
            # Start verification after GUI loads
            self.root.after(1000, self.start_verification)
            self.root.mainloop()
        except Exception as e:
            print(f"Error running GUI: {e}")
            self.close()


# Backward compatibility alias
StudentVerificationGUI = StudentVerificationView
