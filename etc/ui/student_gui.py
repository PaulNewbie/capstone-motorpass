# ui/student_gui.py - Responsive Student GUI for 15" Square Touch Screen (1024x768)

import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
from datetime import datetime
import os
from PIL import Image, ImageTk
from typing import Dict
import sys
import queue

from refresh import add_refresh_to_window

class StudentVerificationGUI:
    def __init__(self, verification_function):
        self.root = tk.Tk()
        self.verification_function = verification_function
        self.verification_complete = False  # Initialize BEFORE other methods
        self.setup_window()
        if add_refresh_to_window:
            add_refresh_to_window(self.root)
        self.create_variables()
        self.create_interface()
        
    def setup_window(self):
        """Setup the main window with responsive fullscreen for touch screen"""
        self.root.title("MotorPass - Student/Staff Verification")
        self.root.configure(bg='#8B4513')
        
        # Get screen dimensions
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        
        # Calculate aspect ratio to determine display type
        aspect_ratio = self.screen_width / self.screen_height
        self.is_square_display = abs(aspect_ratio - 1.0) < 0.3  # Within 30% of square (1024x768 = 1.33)
        
        # Set fullscreen geometry
        self.root.geometry(f"{self.screen_width}x{self.screen_height}")
        self.root.resizable(False, False)
        
        # Make window fullscreen and hide taskbar
        try:
            # Try Windows method first
            self.root.state('zoomed')
            # Hide taskbar by making window truly fullscreen
            self.root.attributes('-fullscreen', True)
        except:
            # Fallback for other platforms
            try:
                self.root.attributes('-zoomed', True)
                self.root.attributes('-fullscreen', True)
            except:
                # Final fallback - just maximize
                self.root.state('normal')
                self.root.geometry(f"{self.screen_width}x{self.screen_height}+0+0")
        
        # Bind Escape key to exit fullscreen (for testing/admin access)
        self.root.bind('<Escape>', self.toggle_fullscreen_and_close)
        # Also bind F11 for fullscreen toggle
        self.root.bind('<F11>', self.toggle_fullscreen)
        
    def toggle_fullscreen(self, event=None):
        """Toggle fullscreen mode - useful for admin access or testing"""
        try:
            current_state = self.root.attributes('-fullscreen')
            self.root.attributes('-fullscreen', not current_state)
            
            if current_state:
                print("Exited fullscreen mode (Taskbar visible)")
            else:
                print("Entered fullscreen mode (Taskbar hidden)")
                
        except Exception as e:
            print(f"Error toggling fullscreen: {e}")
            
    def toggle_fullscreen_and_close(self, event=None):
        """Handle escape key - close the application"""
        self.close()
        
    def create_variables(self):
        """Create all tkinter variables"""
        self.helmet_status = tk.StringVar(value="PENDING")
        self.fingerprint_status = tk.StringVar(value="PENDING") 
        self.license_status = tk.StringVar(value="PENDING")
        self.current_step = tk.StringVar(value="🚀 Starting verification process...")
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
        except tk.TclError:
            # Widget has been destroyed
            pass
        except Exception as e:
            # Handle any other errors
            pass
    
    def create_interface(self):
        """Create the responsive main interface"""
        # Main container
        main_container = tk.Frame(self.root, bg='#8B4513')
        main_container.pack(fill="both", expand=True)
        
        # Header
        self.create_header(main_container)
        
        # Content area with responsive padding
        content_padding_x = max(20, int(self.screen_width * 0.02))
        content_padding_y = max(15, int(self.screen_height * 0.02))
        
        content_frame = tk.Frame(main_container, bg='#8B4513')
        content_frame.pack(fill="both", expand=True, padx=content_padding_x, pady=content_padding_y)
        
        # Title with responsive font
        title_font_size = max(24, int(min(self.screen_width, self.screen_height) / 32))
        self.main_title_label = tk.Label(content_frame, text="STUDENT/STAFF VERIFICATION", 
                      font=("Arial", title_font_size, "bold"), fg="#FFFFFF", bg='#8B4513')
        self.main_title_label.pack(pady=(0, max(15, int(self.screen_height * 0.02))))
        
        # Main content panels
        panels_container = tk.Frame(content_frame, bg='#8B4513')
        panels_container.pack(fill="both", expand=True)
        
        # Left panel - Status indicators WITH user info
        self.create_left_panel(panels_container)
        
        # Right panel - Camera Feed (empty)
        self.create_right_panel(panels_container)
        
        # Footer
        self.create_footer(main_container)
        
    def create_header(self, parent):
        """Create responsive header with logo and title"""
        # Calculate responsive header height
        header_height = max(80, int(self.screen_height * 0.11))
        
        header = tk.Frame(parent, bg='#46230a', height=header_height)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        # Header content with responsive padding
        header_padding = max(15, int(self.screen_width * 0.015))
        header_content = tk.Frame(header, bg='#46230a')
        header_content.pack(fill="both", expand=True, padx=header_padding, pady=max(8, int(header_height * 0.1)))
        
        # Logo container with responsive sizing
        logo_size = max(60, int(header_height * 0.75))
        logo_container = tk.Frame(header_content, bg='#46230a')
        logo_container.pack(side="left", padx=(0, max(12, int(self.screen_width * 0.012))))
        
        # Try to load logo
        logo_loaded = False
        logo_paths = ["assets/logo.png", "logo.png", "../assets/logo.png"]
        
        for logo_path in logo_paths:
            if os.path.exists(logo_path):
                try:
                    logo_img = Image.open(logo_path)
                    logo_img = logo_img.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
                    self.logo_photo = ImageTk.PhotoImage(logo_img)
                    logo_label = tk.Label(logo_container, image=self.logo_photo, bg='#46230a')
                    logo_label.pack()
                    logo_loaded = True
                    break
                except:
                    pass
        
        if not logo_loaded:
            # Fallback text logo with responsive sizing
            logo_frame = tk.Frame(logo_container, bg='#DAA520', width=logo_size, height=logo_size)
            logo_frame.pack()
            logo_frame.pack_propagate(False)
            fallback_font_size = max(20, int(logo_size * 0.35))
            tk.Label(logo_frame, text="MP", font=("Arial", fallback_font_size, "bold"), 
                    fg="#46230a", bg="#DAA520").place(relx=0.5, rely=0.5, anchor="center")
        
        # Title section with responsive fonts
        title_frame = tk.Frame(header_content, bg='#46230a')
        title_frame.pack(side="left", fill="both", expand=True)
        
        # Responsive font sizes based on screen width
        main_title_font = max(20, int(self.screen_width / 40))
        subtitle_font = max(9, int(self.screen_width / 100))
        
        tk.Label(title_frame, text="MotorPass", font=("Arial", main_title_font, "bold"), 
                fg="#DAA520", bg='#46230a').pack(anchor="w")
        tk.Label(title_frame, text="We secure the safeness of your motorcycle inside our campus",
                font=("Arial", subtitle_font), fg="#FFFFFF", bg='#46230a').pack(anchor="w")
        
        # Clock with responsive sizing
        clock_width = max(140, int(self.screen_width * 0.14))
        clock_height = max(65, int(header_height * 0.8))
        
        clock_frame = tk.Frame(header_content, bg='#46230a', bd=2, relief='solid',
                              width=clock_width, height=clock_height)
        clock_frame.pack(side="right")
        clock_frame.pack_propagate(False)
        
        # Responsive clock fonts
        time_font_size = max(14, int(self.screen_width / 55))
        date_font_size = max(9, int(self.screen_width / 100))
        
        tk.Label(clock_frame, textvariable=self.time_string, font=("Arial", time_font_size, "bold"), 
                fg="#DAA520", bg='#46230a').pack(padx=10, pady=(8, 3))
        tk.Label(clock_frame, textvariable=self.date_string, font=("Arial", date_font_size), 
                fg="#FFFFFF", bg='#46230a').pack(padx=10, pady=(0, 8))

    def create_left_panel(self, parent):
        """Create responsive left panel with ONLY verification steps - NO user info"""
        left_frame = tk.Frame(parent, bg='#8B4513')
        left_frame.pack(side="left", fill="both", expand=True)
        
        # Verification steps container
        steps_container = tk.Frame(left_frame, bg='white', relief='raised', bd=3)
        steps_container.pack(fill="both", expand=True)
        
        # Title with responsive font
        title_font_size = max(18, int(self.screen_width / 45))
        title_padding_y = max(18, int(self.screen_height * 0.025))
        
        tk.Label(steps_container, text="VERIFICATION STEPS", 
                font=("Arial", title_font_size, "bold"), fg="#333333", bg='white').pack(pady=title_padding_y)
        
        # Steps content with responsive padding
        steps_padding_x = max(20, int(self.screen_width * 0.02))
        steps_padding_y = max(15, int(self.screen_height * 0.02))
        
        steps_frame = tk.Frame(steps_container, bg='white')
        steps_frame.pack(fill="both", expand=True, padx=steps_padding_x, pady=(0, steps_padding_y))
        
        # Create the three verification steps using existing create_status_item method
        self.create_status_item(steps_frame, "🪖 HELMET CHECK", self.helmet_status, 'helmet')
        self.create_status_item(steps_frame, "🔒 FINGERPRINT SCAN", self.fingerprint_status, 'fingerprint')
        self.create_status_item(steps_frame, "📄 LICENSE VERIFICATION", self.license_status, 'license')
        
        # Current Step Display with responsive font
        current_step_padding = max(25, int(self.screen_height * 0.035))
        current_step_font = max(11, int(self.screen_width / 75))
        
        self.current_step_label = tk.Label(steps_container, 
            textvariable=self.current_step, 
            font=("Arial", current_step_font), 
            fg="#1565c0", 
            bg='white', 
            wraplength=max(300, int(self.screen_width * 0.3)),
            justify="center")
        self.current_step_label.pack(pady=current_step_padding)

        
    def create_status_item(self, parent, label_text, status_var, row):
        """Create individual status item with responsive design"""
        # Container for this item with responsive spacing
        item_spacing_y = max(12, int(self.screen_height * 0.015))
        item_frame = tk.Frame(parent, bg='white')
        item_frame.pack(fill="x", pady=item_spacing_y)
        
        # Label with responsive typography
        label_font_size = max(12, int(self.screen_width / 70))
        tk.Label(item_frame, text=label_text, font=("Arial", label_font_size, "bold"), 
                fg="#333333", bg='white').pack(side="left")
        
        # Status badge with responsive sizing
        badge_font_size = max(10, int(self.screen_width / 85))
        badge_padding_x = max(15, int(self.screen_width * 0.015))
        badge_padding_y = max(6, int(self.screen_height * 0.008))
        
        badge = tk.Label(item_frame, text="PENDING", font=("Arial", badge_font_size, "bold"), 
                        fg="#FFFFFF", bg="#95a5a6", padx=badge_padding_x, pady=badge_padding_y, relief='flat')
        badge.pack(side="right", padx=(0, max(8, int(self.screen_width * 0.008))))
        
        # Status icon with responsive size
        icon_font_size = max(14, int(self.screen_width / 60))
        icon_spacing = max(12, int(self.screen_width * 0.012))
        
        icon_label = tk.Label(item_frame, text="⏸", font=("Arial", icon_font_size), 
                             fg="#95a5a6", bg='white')
        icon_label.pack(side="right", padx=(0, icon_spacing))
        
        # Store references
        setattr(self, f"badge_{row}", badge)
        setattr(self, f"icon_{row}", icon_label)
        
        # Update display when status changes
        status_var.trace_add("write", lambda *args: self.update_status_display(row, status_var.get()))
    
    def update_status_display(self, row, status):
        """Update status display colors and icons with improved styling"""
        badge = getattr(self, f"badge_{row}", None)
        icon = getattr(self, f"icon_{row}", None)
        
        if not badge or not icon:
            return
            
        status_configs = {
            "VERIFIED": ("#27ae60", "✔️", "#27ae60"),      # Green checkmark emoji
            "VALID": ("#27ae60", "✔️", "#27ae60"),
            "PROCESSING": ("#f39c12", "[-]", "#f39c12"),    # Keep hourglass
            "CHECKING": ("#3498db", "?", "#3498db"),      # Keep magnifying glass
            "FAILED": ("#e74c3c", "❌", "#e74c3c"),         # X emoji
            "INVALID": ("#e74c3c", "❌", "#e74c3c"),
            "PENDING": ("#95a5a6", "...", "#95a5a6"),       # Pause emoji
            "EXPIRED": ("#e74c3c", "⚠️", "#e74c3c")        # Warning emoji
        }
        
        config = status_configs.get(status.upper(), ("#95a5a6", "[-]", "#95a5a6"))
        
        # Update badge with responsive styling
        badge_font_size = max(10, int(self.screen_width / 85))
        badge.config(bg=config[0], text=status.upper(), font=("Arial", badge_font_size, "bold"))
        icon_font_size = max(14, int(self.screen_width / 60))
        icon.config(text=config[1], fg=config[2], font=("Arial", icon_font_size))

    def create_right_panel(self, parent):
        """Create responsive right panel with student/staff information"""
        right_frame = tk.Frame(parent, bg='#8B4513')
        right_frame.pack(side="right", fill="both", expand=True)
        
        # Details container
        details_container = tk.Frame(right_frame, bg='white', relief='raised', bd=3)
        details_container.pack(fill="both", expand=True)
        
        # Title with responsive font
        title_font_size = max(16, int(self.screen_width / 50))
        title_padding_y = max(15, int(self.screen_height * 0.02))
        
        self.user_type_title_label = tk.Label(details_container, text="STUDENT/STAFF INFORMATION", 
            font=("Arial", title_font_size, "bold"), fg="#333333", bg='white')
        self.user_type_title_label.pack(pady=title_padding_y)
        
        # Details content with responsive padding
        details_padding_x = max(15, int(self.screen_width * 0.015))
        details_padding_y = max(8, int(self.screen_height * 0.01))
        
        self.details_content = tk.Frame(details_container, bg='white')
        self.details_content.pack(fill="both", expand=True, padx=details_padding_x, pady=details_padding_y)
        
        # Initial message with responsive font
        message_font_size = max(11, int(self.screen_width / 80))
        self.initial_message = tk.Label(self.details_content, 
                                       text="Starting verification...\nPlease check the terminal window for camera operations.", 
                                       font=("Arial", message_font_size), fg="#666666", bg='white', justify="center")
        self.initial_message.pack(expand=True)
        
        # Hidden panels for later use
        self.create_hidden_panels()
    
    def create_footer(self, parent):
        """Create responsive footer"""
        # Calculate responsive footer height
        footer_height = max(50, int(self.screen_height * 0.07))
        
        footer = tk.Frame(parent, bg='#46230a', height=footer_height)
        footer.pack(fill="x")
        footer.pack_propagate(False)
        
        # Responsive footer text font
        footer_font_size = max(10, int(self.screen_width / 85))
        
        footer_text = "🪖 Helmet Check → 🔒 Fingerprint Scan → 📄 License Verification | ESC to exit"
        tk.Label(footer, text=footer_text, font=("Arial", footer_font_size), 
                fg="#FFFFFF", bg='#46230a').pack(expand=True)
                
    def create_hidden_panels(self):
        """Create panels that will be shown later with responsive design"""
        # User info panel
        self.user_info_panel_right = tk.Frame(self.details_content, bg='#e3f2fd', relief='ridge', bd=2)
        
        # Responsive font for panel titles
        panel_title_font = max(13, int(self.screen_width / 65))
        panel_title_padding = max(12, int(self.screen_height * 0.015))
        
        tk.Label(self.user_info_panel_right, text="👤 USER DETAILS", 
                font=("Arial", panel_title_font, "bold"), fg="#1565c0", bg='#e3f2fd').pack(pady=panel_title_padding)
        
        self.user_details_frame_right = tk.Frame(self.user_info_panel_right, bg='#e3f2fd')
        details_padding_x = max(15, int(self.screen_width * 0.015))
        details_padding_y = max(15, int(self.screen_height * 0.015))
        self.user_details_frame_right.pack(padx=details_padding_x, pady=(0, details_padding_y))

    def show_user_info(self, user_info):
        """Display user information in RIGHT panel with responsive design"""
        try:
            # Hide initial message
            if hasattr(self, 'initial_message'):
                self.initial_message.pack_forget()
                
            user_type = user_info.get('user_type', 'STUDENT')
        
            if user_type == 'STAFF':
                # Update main title
                if hasattr(self, 'main_title_label'):
                    self.main_title_label.config(text="STAFF VERIFICATION")
                # Update right panel title
                if hasattr(self, 'user_type_title_label'):
                    self.user_type_title_label.config(text="STAFF INFORMATION")
            else:
                # Update main title
                if hasattr(self, 'main_title_label'):
                    self.main_title_label.config(text="STUDENT VERIFICATION")
                # Update right panel title
                if hasattr(self, 'user_type_title_label'):
                    self.user_type_title_label.config(text="STUDENT INFORMATION")
                
            # Clear previous details
            for widget in self.user_details_frame_right.winfo_children():
                widget.destroy()
            
            # Create info labels with responsive fonts
            label_font_size = max(10, int(self.screen_width / 85))
            value_font_size = max(10, int(self.screen_width / 85))
            
            info_items = [
                ("Name:", user_info.get('name', 'N/A')),
                ("Student ID:", user_info.get('student_id', 'N/A')),
                ("Course:", user_info.get('course', 'N/A')),
                ("User Type:", user_info.get('user_type', 'STUDENT'))
            ]
            
            for label, value in info_items:
                row_spacing = max(2, int(self.screen_height * 0.003))
                row = tk.Frame(self.user_details_frame_right, bg='#e3f2fd')
                row.pack(fill="x", pady=row_spacing)
                
                label_width = max(10, int(self.screen_width / 85))
                tk.Label(row, text=label, font=("Arial", label_font_size, "bold"), 
                        fg="#333333", bg='#e3f2fd', width=label_width, anchor="w").pack(side="left")
                tk.Label(row, text=value, font=("Arial", value_font_size), 
                        fg="#1565c0", bg='#e3f2fd').pack(side="left", padx=(8, 0))
            
            # Show the user info panel with responsive spacing
            panel_spacing_y = max(15, int(self.screen_height * 0.02))
            self.user_info_panel_right.pack(fill="both", expand=True, pady=(0, panel_spacing_y))
        except Exception as e:
            print(f"Error showing user info: {e}")

    def show_final_result(self, result):
        """Show final verification result - Clean & Professional Design"""
        try:
            self.verification_complete = True
            
            # Clean, centered result card with golden background
            card_width = 600
            card_height = 400
            
            # Create card with golden background and raised border
            result_card = tk.Frame(self.root, bg='#FFD700', relief='raised', bd=4)
            result_card.place(relx=0.5, rely=0.5, anchor='center', 
                             width=card_width, height=card_height)
            
            # Inner content area with padding
            content = tk.Frame(result_card, bg='#FFD700')
            content.pack(fill='both', expand=True, padx=20, pady=20)
            
            if result.get('verified', False):
                # ===== SUCCESS LAYOUT =====
                
                # Success icon
                icon_label = tk.Label(content, text="✓", 
                                    font=("Arial", 80, "bold"), 
                                    fg="#4CAF50", bg='#FFD700')
                icon_label.pack(pady=(40, 20))
                
                # Title
                title = tk.Label(content, text="Verification Successful", 
                               font=("Arial", 28, "bold"), 
                               fg="#2E7D32", bg='#FFD700')
                title.pack(pady=(0, 25))
                
                # Format name
                name = result.get('name', 'User')
                if ',' in name:
                    parts = name.split(',')
                    if len(parts) >= 2:
                        name = f"{parts[1].strip()} {parts[0].strip()}"
                
                # Welcome message
                welcome = tk.Label(content, text=f"Welcome, {name}", 
                                 font=("Arial", 20), 
                                 fg="#333333", bg='#FFD700')
                welcome.pack(pady=(0, 15))
                
                # Time info with icon
                time_action = result.get('time_action', 'IN')
                timestamp = result.get('timestamp', 'N/A')
                time_icon = "🕐" if time_action == 'IN' else "🕐"
                
                time_frame = tk.Frame(content, bg='#E8F5E9', bd=0)
                time_frame.pack(pady=(10, 0), padx=40, fill='x')
                
                time_label = tk.Label(time_frame, 
                                    text=f"{time_icon}  Time {time_action}: {timestamp}", 
                                    font=("Arial", 16), 
                                    fg="#1B5E20", bg='#E8F5E9',
                                    pady=12)
                time_label.pack()
                
            else:
                # ===== FAILURE LAYOUT =====
                
                # Error icon
                icon_label = tk.Label(content, text="✕", 
                                    font=("Arial", 80, "bold"), 
                                    fg="#F44336", bg='#FFD700')
                icon_label.pack(pady=(40, 20))
                
                # Title
                title = tk.Label(content, text="Verification Failed", 
                               font=("Arial", 28, "bold"), 
                               fg="#C62828", bg='#FFD700')
                title.pack(pady=(0, 30))
                
                # Error message box
                error_frame = tk.Frame(content, bg='#FFEBEE', bd=0)
                error_frame.pack(pady=(0, 20), padx=50, fill='x')
                
                reason_text = result.get('reason', 'Unknown error')
                reason = tk.Label(error_frame, 
                                text=reason_text, 
                                font=("Arial", 16), 
                                fg="#C62828", bg='#FFEBEE',
                                wraplength=480,
                                justify='center',
                                pady=15)
                reason.pack()
                
                # Help text
                help_text = tk.Label(content, 
                                   text="Please contact security if you need assistance", 
                                   font=("Arial", 12), 
                                   fg="#757575", bg='#FFD700')
                help_text.pack(pady=(10, 0))
            
            # Auto close with timing
            close_delay = 4000 if result.get('verified', False) else 5000
            self.root.after(close_delay, self.close)
            
        except Exception as e:
            print(f"Error showing final result: {e}")
            self.close()
                    
    def update_status(self, updates):
        """Update status from verification thread"""
        try:
            for key, value in updates.items():
                if key == 'helmet_status':
                    self.helmet_status.set(value)
                elif key == 'fingerprint_status':
                    self.fingerprint_status.set(value)
                elif key == 'license_status':
                    self.license_status.set(value)
                elif key == 'current_step':
                    self.current_step.set(value)
                    self.root.update_idletasks()  # Force GUI update
                elif key == 'user_info':
                    self.show_user_info(value)
                elif key == 'verification_summary':
                    # Remove verification summary - just pass
                    pass
                elif key == 'final_result':
                    self.show_final_result(value)
        except Exception as e:
            print(f"Error updating status: {e}")

    def start_verification(self):
        """Start verification in separate thread"""
        self.current_step.set("🚀 Initializing verification process...")
        
        # Run verification in thread
        thread = threading.Thread(target=self.run_verification_thread, daemon=True)
        thread.start()

    def run_verification_thread(self):
        """Run verification and update GUI"""
        # Call the verification function with callback
        result = self.verification_function(self.update_status_callback)
        
        # Show final result
        self.root.after(0, lambda: self.update_status({'final_result': result}))

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
            
            # Cancel any pending after callbacks
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
            print(f"📱 Responsive Mode: {self.screen_width}x{self.screen_height}")
            if self.is_square_display:
                print(f"📺 Display Type: Square/4:3 Touch Screen Optimized")
            print(f"{'='*60}")
            
            # Bind escape key
            self.root.bind('<Escape>', lambda e: self.close())
            
            # Start verification after GUI loads
            self.root.after(1000, self.start_verification)
            
            # Start main loop
            self.root.mainloop()
        except Exception as e:
            print(f"Error running GUI: {e}")
            self.close()
