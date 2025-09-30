# ui/views/student_view.py - PROPERLY ORGANIZED: Uses reusable components

import tkinter as tk
from datetime import datetime
import threading
from etc.ui.components.verification_components import VerificationUIComponents
from etc.ui.business.student_operations import StudentVerificationManager

try:
    from etc.utils.window_utils import add_refresh_to_window
    refresh_available = True
except ImportError:
    refresh_available = False

class StudentVerificationView:
    """Student Verification GUI using properly organized reusable components"""
    
    def __init__(self, verification_function):
        self.verification_function = verification_function
        self.verification_complete = False
        self.verification_manager = StudentVerificationManager()
        
        # Screen info for responsive design
        self.screen_info = self.get_screen_info()
        self.calculate_responsive_padding()
        
        # Create window
        self.create_window()
        
        # Add refresh functionality if available
        if refresh_available:
            add_refresh_to_window(self.root)
            
        self.create_variables()
        self.create_interface()
        
        # Bind keys
        self.root.bind('<Escape>', lambda e: self.close())
        self.root.bind('<F11>', self.toggle_fullscreen)
        
    def get_screen_info(self):
        """Get screen information for responsive design"""
        root = tk.Tk()
        root.withdraw()
        
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        is_square_display = abs(screen_width - screen_height) < 200
        
        root.destroy()
        
        return {
            'screen_width': screen_width,
            'screen_height': screen_height,
            'is_square_display': is_square_display
        }
    
    def calculate_responsive_padding(self):
        """Calculate responsive padding sizes"""
        screen_width = self.screen_info['screen_width']
        screen_height = self.screen_info['screen_height']
        
        self.padding_sizes = {
            'content_x': max(15, int(screen_width * 0.015)),
            'content_y': max(10, int(screen_height * 0.012)),
            'section_spacing': max(15, int(min(screen_width, screen_height) * 0.02))
        }
    
    def create_window(self):
        """Create main window"""
        self.root = tk.Tk()
        self.root.title("MotorPass - Student/Staff Verification")
        self.root.configure(bg='#8B4513')
        
        # Fullscreen
        self.root.attributes('-fullscreen', True)
        self.root.geometry(f"{self.screen_info['screen_width']}x{self.screen_info['screen_height']}+0+0")
        
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
        """Create interface using reusable components"""
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
        
        # Right panel - USE reusable student info component
        self.create_student_info_panel(panels_container)
        
        # Footer - USE reusable component
        VerificationUIComponents.create_verification_footer(
            parent=main_container,
            screen_info=self.screen_info,
            footer_text="Helmet Check → Fingerprint Scan → License Verification | ESC to exit"
        )
        
    def create_status_panel(self, parent):
        """Create simple status panel - no user info cluttering"""
        left_frame = tk.Frame(parent, bg='#8B4513')
        left_frame.pack(side="left", fill="both", expand=True, 
                       padx=(0, self.padding_sizes['section_spacing']))
        
        # Define status variables for reusable component
        status_vars = {
            'helmet': ("🪖 HELMET CHECK:", self.helmet_status),
            'fingerprint': ("👆 FINGERPRINT:", self.fingerprint_status),
            'license': ("🪪 LICENSE CHECK:", self.license_status)
        }
        
        # USE reusable status panel component - clean and simple
        VerificationUIComponents.create_status_panel(
            parent=left_frame,
            status_vars=status_vars,
            screen_info=self.screen_info,
            title="VERIFICATION STATUS"
        )

    def create_student_info_panel(self, parent):
        """Create clean student info panel using reusable component"""
        right_frame = tk.Frame(parent, bg='#8B4513')
        right_frame.pack(side="right", fill="both", expand=True)
        
        # USE clean student info component
        student_info_components = VerificationUIComponents.create_student_info_panel(
            parent=right_frame,
            screen_info=self.screen_info,
            current_step_var=self.current_step
        )
        
        # Store references for later use
        self.student_welcome_label = student_info_components['welcome_label']
        self.student_details_frame = student_info_components['details_frame']
        self.student_welcome_card = student_info_components['welcome_card']

    def show_user_info(self, user_info):
        """Display user info - clean and focused"""
        # Update the right panel with clean student information
        VerificationUIComponents.update_student_info_display(
            details_frame=self.student_details_frame,
            welcome_label=self.student_welcome_label,
            step_label=None,  # Not needed anymore
            user_info=user_info,
            screen_info=self.screen_info,
            welcome_card=self.student_welcome_card
        )

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
