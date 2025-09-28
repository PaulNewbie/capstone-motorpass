# ui/views/guest_view.py - Refactored GuestGUI using Component-Based Architecture
# CLEAN UI ONLY - Uses existing components from ui_components.py and window_helpers.py

import tkinter as tk
from tkinter import ttk
import threading
from datetime import datetime
import os
from PIL import Image, ImageTk
import queue

# Import our reusable components - NO DUPLICATED CODE
from ui.components.window_helpers import WindowManager, ResponsiveCalculator
from ui.components.ui_components import UIComponents
from refresh import add_refresh_to_window


class GuestVerificationView:
    """Refactored GuestGUI - Clean UI using reusable components, NO duplicated functions"""
    
    def __init__(self, verification_function):
        self.root = tk.Tk()
        self.verification_function = verification_function
        self.verification_complete = False
        
        # Use WindowManager for setup - REUSE existing component
        self.screen_info = WindowManager.setup_fullscreen_window(
            self.root, 
            "MotorPass - VISITOR Verification",
            '#8B4513'
        )
        
        # Extract screen info for convenience
        self.screen_width = self.screen_info['screen_width']
        self.screen_height = self.screen_info['screen_height']
        self.is_square_display = self.screen_info['is_square_display']
        self.display_size = self.screen_info['display_size']
        
        # Use ResponsiveCalculator for font sizes - REUSE existing component
        self.font_sizes = ResponsiveCalculator.calculate_font_sizes(self.display_size)
        self.padding_sizes = ResponsiveCalculator.calculate_padding_sizes(
            self.screen_width, self.screen_height
        )
        
        # Add refresh functionality if available
        if add_refresh_to_window:
            add_refresh_to_window(self.root)
        
        # Setup key bindings for fullscreen control
        self.setup_key_bindings()
        
        # Create UI
        self.create_variables()
        self.create_interface()
        
    def setup_key_bindings(self):
        """Setup keyboard shortcuts - REUSE from legacy pattern"""
        # Bind F11 for fullscreen toggle (for testing/admin access)
        self.root.bind('<F11>', self.toggle_fullscreen)
        # Bind Ctrl+C for emergency abort
        self.root.bind('<Control-c>', self.emergency_abort)
        
    def toggle_fullscreen(self, event=None):
        """Toggle fullscreen mode - REUSE from legacy pattern"""
        try:
            current_state = self.root.attributes('-fullscreen')
            self.root.attributes('-fullscreen', not current_state)
        except:
            pass
    
    def emergency_abort(self, event=None):
        """Emergency abort - REUSE from legacy pattern"""
        self.verification_complete = True
        self.root.quit()
        
    def create_variables(self):
        """Create UI variables - REUSE from legacy pattern"""
        self.current_step = tk.StringVar(value="🔄 Initializing visitor verification system...")
        self.guest_info = tk.StringVar(value="👤 Ready for visitor registration")
        self.time_string = tk.StringVar()
        self.date_string = tk.StringVar()
        
        # Additional variables for guest verification
        self.helmet_status = tk.StringVar(value="⏳ Waiting...")
        self.license_status = tk.StringVar(value="⏳ Waiting...")
        self.registration_status = tk.StringVar(value="⏳ Waiting...")
        
        # Start time update
        self.update_time()
        
    def update_time(self):
        """Update time display - REUSE from legacy pattern"""
        try:
            now = datetime.now()
            self.time_string.set(now.strftime('%I:%M:%S %p'))
            self.date_string.set(now.strftime('%A, %B %d, %Y'))
            self._update_timer = self.root.after(1000, self.update_time)
        except tk.TclError:
            pass
        except Exception as e:
            pass
    
    def create_interface(self):
        """Create the responsive main interface - REUSE UI patterns"""
        # Main container
        main_container = tk.Frame(self.root, bg='#8B4513')
        main_container.pack(fill="both", expand=True)
        
        # Header
        self.create_header(main_container)
        
        # Content area with responsive padding - USE existing padding calculation
        content_frame = tk.Frame(main_container, bg='#8B4513')
        content_frame.pack(fill="both", expand=True, 
                          padx=self.padding_sizes['content_x'], 
                          pady=self.padding_sizes['content_y'])
        
        # Title with responsive font - USE existing font calculation
        title_label = tk.Label(content_frame, 
                              text="VISITOR VERIFICATION", 
                              font=("Arial", self.font_sizes['title'], "bold"), 
                              fg="#FFFFFF", bg='#8B4513')
        title_label.pack(pady=(0, self.padding_sizes['title_padding']))
        
        # Main content panels
        panels_container = tk.Frame(content_frame, bg='#8B4513')
        panels_container.pack(fill="both", expand=True)
        
        # Left panel - Status indicators
        self.create_left_panel(panels_container)
        
        # Right panel - Guest information
        self.create_right_panel(panels_container)
        
        # Footer
        self.create_footer(main_container)
        
    def create_header(self, parent):
        """Create responsive header - USE existing responsive patterns"""
        # Calculate responsive header height - REUSE calculation pattern
        header_height = max(80, int(self.screen_height * 0.11))
        
        header = tk.Frame(parent, bg='#46230a', height=header_height)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        # Header content with responsive padding
        header_padding = max(15, int(self.screen_width * 0.015))
        header_content = tk.Frame(header, bg='#46230a')
        header_content.pack(fill="both", expand=True, padx=header_padding, pady=10)
        
        # Logo and title section
        logo_section = tk.Frame(header_content, bg='#46230a')
        logo_section.pack(side="left", fill="y")
        
        # Logo placeholder (visitor icon)
        logo_size = max(40, int(header_height * 0.6))
        logo_label = tk.Label(logo_section, text="🏪", 
                             font=("Arial", logo_size), fg="#D4AF37", bg='#46230a')
        logo_label.pack(side="left", pady=5)
        
        # Title
        title_font_size = max(16, int(header_height * 0.3))
        title_label = tk.Label(logo_section, text="MotorPass VISITOR", 
                              font=("Arial", title_font_size, "bold"), 
                              fg="#FFFFFF", bg='#46230a')
        title_label.pack(side="left", padx=(10, 0), pady=5)
        
        # Time display section - USE existing time variables
        time_section = tk.Frame(header_content, bg='#46230a')
        time_section.pack(side="right", fill="y")
        
        time_font_size = max(12, int(header_height * 0.25))
        time_label = tk.Label(time_section, textvariable=self.time_string,
                             font=("Arial", time_font_size, "bold"), 
                             fg="#D4AF37", bg='#46230a')
        time_label.pack(anchor="ne")
        
        date_font_size = max(8, int(header_height * 0.18))
        date_label = tk.Label(time_section, textvariable=self.date_string,
                             font=("Arial", date_font_size), 
                             fg="#FFFFFF", bg='#46230a')
        date_label.pack(anchor="ne")
        
    def create_left_panel(self, parent):
        """Create left panel with status indicators - REUSE UI patterns"""
        # Calculate responsive panel width
        panel_width = max(350, int(self.screen_width * 0.45))
        
        left_frame = tk.Frame(parent, bg='#2E1810', width=panel_width)
        left_frame.pack(side="left", fill="y", padx=(0, 15))
        left_frame.pack_propagate(False)
        
        # Panel title
        title_font_size = max(14, int(self.display_size / 60))
        title_label = tk.Label(left_frame, text="VERIFICATION STATUS", 
                              font=("Arial", title_font_size, "bold"), 
                              fg="#D4AF37", bg='#2E1810')
        title_label.pack(pady=20)
        
        # Status indicators container
        status_container = tk.Frame(left_frame, bg='#2E1810')
        status_container.pack(fill="both", expand=True, padx=20)
        
        # Create status indicators using reusable pattern
        self.create_status_indicator(status_container, "🪖 HELMET CHECK", self.helmet_status)
        self.create_status_indicator(status_container, "🆔 LICENSE CHECK", self.license_status)
        self.create_status_indicator(status_container, "📝 REGISTRATION", self.registration_status)
        
        # Current step display
        step_frame = tk.Frame(status_container, bg='#3E2820', relief="ridge", bd=2)
        step_frame.pack(fill="x", pady=20)
        
        step_title = tk.Label(step_frame, text="CURRENT STEP", 
                             font=("Arial", 10, "bold"), 
                             fg="#D4AF37", bg='#3E2820')
        step_title.pack(pady=(10, 5))
        
        step_label = tk.Label(step_frame, textvariable=self.current_step, 
                             font=("Arial", 9), fg="#FFFFFF", bg='#3E2820',
                             wraplength=panel_width-40, justify="center")
        step_label.pack(pady=(0, 10), padx=10)
        
    def create_status_indicator(self, parent, title, status_var):
        """Create a status indicator - REUSABLE component pattern"""
        indicator_frame = tk.Frame(parent, bg='#3E2820', relief="ridge", bd=1)
        indicator_frame.pack(fill="x", pady=8)
        
        title_label = tk.Label(indicator_frame, text=title, 
                              font=("Arial", 10, "bold"), 
                              fg="#D4AF37", bg='#3E2820')
        title_label.pack(pady=(8, 4))
        
        status_label = tk.Label(indicator_frame, textvariable=status_var, 
                               font=("Arial", 9), fg="#FFFFFF", bg='#3E2820')
        status_label.pack(pady=(0, 8))
        
    def create_right_panel(self, parent):
        """Create right panel with guest information - REUSE UI patterns"""
        right_frame = tk.Frame(parent, bg='#2E1810')
        right_frame.pack(side="right", fill="both", expand=True)
        
        # Panel title
        title_font_size = max(14, int(self.display_size / 60))
        title_label = tk.Label(right_frame, text="VISITOR INFORMATION", 
                              font=("Arial", title_font_size, "bold"), 
                              fg="#D4AF37", bg='#2E1810')
        title_label.pack(pady=20)
        
        # Guest info display
        info_frame = tk.Frame(right_frame, bg='#3E2820', relief="ridge", bd=2)
        info_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Guest info content
        info_content = tk.Frame(info_frame, bg='#3E2820')
        info_content.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Guest status display
        guest_label = tk.Label(info_content, textvariable=self.guest_info, 
                             font=("Arial", 12), fg="#FFFFFF", bg='#3E2820',
                             wraplength=300, justify="center")
        guest_label.pack(expand=True)
        
        # Instructions for visitors
        instructions_text = ("Visitor Registration Process:\n\n"
                           "1. Ensure proper helmet placement\n"
                           "2. Show your license to camera\n"
                           "3. Complete visitor registration\n"
                           "4. Specify office to visit")
        
        instructions_label = tk.Label(info_content, text=instructions_text, 
                                     font=("Arial", 9), fg="#CCCCCC", bg='#3E2820',
                                     justify="left")
        instructions_label.pack(pady=(20, 0))
        
    def create_footer(self, parent):
        """Create footer with system info - REUSE from legacy pattern"""
        footer_height = max(40, int(self.screen_height * 0.05))
        footer = tk.Frame(parent, bg='#1A0F08', height=footer_height)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)
        
        # Footer content
        footer_content = tk.Frame(footer, bg='#1A0F08')
        footer_content.pack(expand=True, fill="both", padx=20)
        
        # System info
        info_text = f"MotorPass Visitor System v2.0 | Screen: {self.screen_width}x{self.screen_height}"
        if self.is_square_display:
            info_text += " (Square)"
        
        info_label = tk.Label(footer_content, text=info_text, 
                             font=("Arial", 8), fg="#666666", bg='#1A0F08')
        info_label.pack(side="left", pady=10)
        
        # Status indicator
        status_label = tk.Label(footer_content, text="● VISITOR MODE", 
                               font=("Arial", 8, "bold"), fg="#FF8C00", bg='#1A0F08')
        status_label.pack(side="right", pady=10)
    
    # ===========================================
    # VERIFICATION UPDATE METHODS - REUSE existing patterns
    # ===========================================
    
    def update_status(self, status_data):
        """Update verification status - USE existing callback pattern"""
        if 'current_step' in status_data:
            self.current_step.set(status_data['current_step'])
        
        if 'helmet' in status_data:
            helmet_text = "✅ DETECTED" if status_data['helmet'] else "❌ NOT DETECTED"
            self.helmet_status.set(helmet_text)
        
        if 'license' in status_data:
            if status_data['license'] == 'checking':
                self.license_status.set("🔄 CHECKING...")
            elif status_data['license']:
                self.license_status.set("✅ VALID")
            else:
                self.license_status.set("❌ INVALID")
        
        if 'registration' in status_data:
            if status_data['registration'] == 'pending':
                self.registration_status.set("🔄 PROCESSING...")
            elif status_data['registration']:
                self.registration_status.set("✅ COMPLETED")
            else:
                self.registration_status.set("❌ INCOMPLETE")
        
        if 'guest_info' in status_data:
            guest_data = status_data['guest_info']
            if isinstance(guest_data, dict):
                info_text = f"👤 {guest_data.get('name', 'Unknown')}\n"
                info_text += f"🚗 Plate: {guest_data.get('plate_number', 'N/A')}\n"
                info_text += f"🏢 Office: {guest_data.get('office', 'N/A')}\n"
                info_text += f"📋 Status: {guest_data.get('status', 'Processing')}"
                self.guest_info.set(info_text)
            else:
                self.guest_info.set(str(guest_data))
    
    def show_verification_result(self, result):
        """Show final verification result - USE existing result pattern"""
        if result.get('verified', False):
            self.current_step.set("✅ VISITOR VERIFICATION SUCCESSFUL!")
            guest_name = result.get('name', 'Visitor')
            office = result.get('office', 'Unknown Office')
            self.guest_info.set(f"Welcome, {guest_name}!\nVisiting: {office}")
        else:
            self.current_step.set(f"❌ VERIFICATION FAILED: {result.get('reason', 'Unknown error')}")
            self.guest_info.set("❌ Access Denied")
        
        # Auto close after delay
        self.root.after(5000, self.close_verification)  # Longer delay for guest
    
    def close_verification(self):
        """Close verification window"""
        self.verification_complete = True
        try:
            self.root.quit()
        except:
            pass
    
    def run_verification(self):
        """Run the verification process - DELEGATE to controller"""
        if self.verification_function:
            # Start verification in separate thread
            verification_thread = threading.Thread(
                target=self.verification_function, 
                args=(self.update_status,),
                daemon=True
            )
            verification_thread.start()
        
        # Start GUI main loop
        self.root.mainloop()


# Factory function for easy integration
def create_guest_verification_gui(verification_function):
    """Factory function to create GuestGUI using reusable components"""
    return GuestVerificationView(verification_function)
