# ui/guest_gui.py - Responsive Guest GUI for 15" Square Touch Screen (1024x768)

import tkinter as tk
from tkinter import ttk
import threading
from datetime import datetime
import os
from PIL import Image, ImageTk
import queue

from refresh import add_refresh_to_window


class GuestVerificationGUI:
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
        self.root.title("MotorPass - VISITOR Verification")
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
        
        # Bind F11 for fullscreen toggle (for testing/admin access)
        self.root.bind('<F11>', self.toggle_fullscreen)
        # Bind Ctrl+C for emergency abort
        self.root.bind('<Control-c>', self.emergency_abort)
        
    def toggle_fullscreen(self, event=None):
        """Toggle fullscreen mode - useful for admin access or testing"""
        try:
            current_state = self.root.attributes('-fullscreen')
            self.root.attributes('-fullscreen', not current_state)
            
            if current_state:
                print("Exited fullscreen mode (Taskbar visible) - Press F11 to return to fullscreen")
            else:
                print("Entered fullscreen mode (Taskbar hidden)")
                
        except Exception as e:
            print(f"Error toggling fullscreen: {e}")
            
    def emergency_abort(self, event=None):
        """Handle Ctrl+C - Emergency abort and close"""
        print("\n🚨 EMERGENCY ABORT - Ctrl+C pressed")
        print("🛑 Stopping all processes and closing...")
        self.safe_close()
        
    def ensure_fullscreen(self):
        """Ensure window stays fullscreen - call this after camera operations"""
        try:
            if not self.root.attributes('-fullscreen'):
                print("🔧 Restoring fullscreen mode after camera operation...")
                self.root.attributes('-fullscreen', True)
                self.root.focus_force()  # Force focus back to our window
                self.root.lift()  # Bring to front
        except Exception as e:
            print(f"Error ensuring fullscreen: {e}")
        
    def create_variables(self):
        """Create all tkinter variables"""
        self.helmet_status = tk.StringVar(value="PENDING")
        self.license_status = tk.StringVar(value="PENDING")
        self.current_step = tk.StringVar(value="🚀 Starting visitor verification...")
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
            pass
        except Exception as e:
            # Handle case where GUI is being destroyed
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
        title_label = tk.Label(content_frame, text="VISITOR VERIFICATION", 
                              font=("Arial", title_font_size, "bold"), fg="#FFFFFF", bg='#8B4513')
        title_label.pack(pady=(0, max(15, int(self.screen_height * 0.02))))
        
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
        """Create responsive left panel with status indicators"""
        left_frame = tk.Frame(parent, bg='#8B4513')
        panel_spacing = max(15, int(self.screen_width * 0.02))
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, panel_spacing))
        
        # Status container with responsive sizing
        status_container = tk.Frame(left_frame, bg='white', relief='raised', bd=3)
        status_container.pack(fill="both", expand=True)
        
        # Title with responsive font
        title_font_size = max(16, int(self.screen_width / 50))
        title_padding_y = max(15, int(self.screen_height * 0.02))
        
        tk.Label(status_container, text="VERIFICATION STATUS", 
                font=("Arial", title_font_size, "bold"), fg="#333333", bg='white').pack(pady=title_padding_y)
        
        # Status items with responsive spacing
        status_padding_x = max(20, int(self.screen_width * 0.02))
        status_padding_y = max(15, int(self.screen_height * 0.02))
        
        status_items_frame = tk.Frame(status_container, bg='white')
        status_items_frame.pack(fill="x", padx=status_padding_x, pady=(0, status_padding_y))
        
        self.create_status_item(status_items_frame, "🪖 HELMET CHECK:", self.helmet_status, 0)
        self.create_status_item(status_items_frame, "🪪 LICENSE SCAN:", self.license_status, 1)

    def create_status_item(self, parent, label_text, status_var, row):
        """Create individual status item with responsive design"""
        # Container for this item with responsive spacing
        item_spacing_y = max(15, int(self.screen_height * 0.02))
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
                        fg="#FFFFFF", bg="#6C757D", padx=badge_padding_x, pady=badge_padding_y, relief='flat')
        badge.pack(side="right", padx=(0, max(8, int(self.screen_width * 0.008))))
        
        # Status icon with responsive size
        icon_font_size = max(14, int(self.screen_width / 60))
        icon_spacing = max(12, int(self.screen_width * 0.012))
        
        icon_label = tk.Label(item_frame, text="⏸", font=("Arial", icon_font_size), 
                             fg="#6C757D", bg='white')
        icon_label.pack(side="right", padx=(0, icon_spacing))
        
        # Store references
        setattr(self, f"badge_{row}", badge)
        setattr(self, f"icon_{row}", icon_label)
        
        # Update display when status changes
        status_var.trace_add("write", lambda *args: self.update_status_display(row, status_var.get()))
    
    def update_status_display(self, row, status):
        """Update status display colors and icons with responsive styling"""
        badge = getattr(self, f"badge_{row}", None)
        icon = getattr(self, f"icon_{row}", None)
        
        if not badge or not icon:
            return
            
        status_configs = {
            "VERIFIED": ("#28a745", "✅", "#28a745"),
            "DETECTED": ("#28a745", "✅", "#28a745"),
            "PROCESSING": ("#FFA500", "⏳", "#FFA500"),
            "CHECKING": ("#17a2b8", "🔍", "#17a2b8"),
            "FAILED": ("#DC3545", "❌", "#DC3545"),
            "NOT DETECTED": ("#DC3545", "❌", "#DC3545"),
            "PENDING": ("#6C757D", "⏸", "#6C757D")
        }
        
        config = status_configs.get(status.upper(), ("#6C757D", "⏸", "#6C757D"))
        
        # Update badge with responsive styling
        badge_font_size = max(10, int(self.screen_width / 85))
        badge.config(bg=config[0], text=status.upper(), font=("Arial", badge_font_size, "bold"))
        icon_font_size = max(14, int(self.screen_width / 60))
        icon.config(text=config[1], fg=config[2], font=("Arial", icon_font_size))
    
    def create_right_panel(self, parent):
        """Create responsive right panel with guest information"""
        right_frame = tk.Frame(parent, bg='#8B4513')
        right_frame.pack(side="right", fill="both", expand=True)
        
        # Details container
        details_container = tk.Frame(right_frame, bg='white', relief='raised', bd=3)
        details_container.pack(fill="both", expand=True)
        
        # Title with responsive font
        title_font_size = max(16, int(self.screen_width / 50))
        title_padding_y = max(15, int(self.screen_height * 0.02))
        
        tk.Label(details_container, text="VISITOR INFORMATION", 
                font=("Arial", title_font_size, "bold"), fg="#333333", bg='white').pack(pady=title_padding_y)
        
        # Details content with responsive padding
        details_padding_x = max(15, int(self.screen_width * 0.015))
        details_padding_y = max(8, int(self.screen_height * 0.01))
        
        self.details_content = tk.Frame(details_container, bg='white')
        self.details_content.pack(fill="both", expand=True, padx=details_padding_x, pady=details_padding_y)
        
        # Initial message with responsive font
        message_font_size = max(11, int(self.screen_width / 80))
        self.initial_message = tk.Label(self.details_content, 
                                       text="Starting visitor verification...\nPlease check the terminal window for camera operations.",
                                       font=("Arial", message_font_size), fg="#666666", bg='white', justify="center")
        self.initial_message.pack(expand=True)
        
        # Hidden panels for later use
        self.create_hidden_panels()
    
    def create_hidden_panels(self):
        """Create panels that will be shown later with responsive design"""
        # Guest info panel
        self.guest_info_panel = tk.Frame(self.details_content, bg='#e8f5e9', relief='ridge', bd=2)
        
        # Responsive font for panel titles
        panel_title_font = max(13, int(self.screen_width / 65))
        panel_title_padding = max(12, int(self.screen_height * 0.015))
        
        tk.Label(self.guest_info_panel, text="👤 GUEST DETAILS", 
                font=("Arial", panel_title_font, "bold"), fg="#2e7d32", bg='#e8f5e9').pack(pady=panel_title_padding)
        
        self.guest_details_frame = tk.Frame(self.guest_info_panel, bg='#e8f5e9')
        details_padding_x = max(15, int(self.screen_width * 0.015))
        details_padding_y = max(15, int(self.screen_height * 0.015))
        self.guest_details_frame.pack(padx=details_padding_x, pady=(0, details_padding_y))
        
        # Verification summary panel
        self.summary_panel = tk.Frame(self.details_content, bg='#f5f5f5', relief='ridge', bd=2)
        
        tk.Label(self.summary_panel, text="🎯 VERIFICATION SUMMARY", 
                font=("Arial", panel_title_font, "bold"), fg="#333333", bg='#f5f5f5').pack(pady=panel_title_padding)
        
        self.summary_frame = tk.Frame(self.summary_panel, bg='#f5f5f5')
        self.summary_frame.pack(padx=details_padding_x, pady=(0, details_padding_y))
    
    def create_footer(self, parent):
        """Create responsive footer"""
        # Calculate responsive footer height
        footer_height = max(50, int(self.screen_height * 0.07))
        
        footer = tk.Frame(parent, bg='#46230a', height=footer_height)
        footer.pack(fill="x")
        footer.pack_propagate(False)
        
        # Responsive footer text font
        footer_font_size = max(10, int(self.screen_width / 85))
        
        footer_text = "🪖 Helmet Required → 📄 License Scan → 📝 Visitor Registration | ESC to exit"
        tk.Label(footer, text=footer_text, font=("Arial", footer_font_size), 
                fg="#FFFFFF", bg='#46230a').pack(expand=True)
    
    def show_guest_info(self, guest_info):
        """Display guest information with responsive design"""
        try:
            self.initial_message.pack_forget()
            
            # Clear previous details
            for widget in self.guest_details_frame.winfo_children():
                widget.destroy()
            
            # Create info labels with responsive fonts
            label_font_size = max(10, int(self.screen_width / 85))
            value_font_size = max(10, int(self.screen_width / 85))
            
            info_items = [
                ("Name:", guest_info.get('name', 'Guest')),
                ("Plate Number:", guest_info.get('plate_number', 'N/A')),
                ("Office Visiting:", guest_info.get('office', 'N/A')),
                ("Status:", guest_info.get('status', 'NEW GUEST'))
            ]
            
            # Add guest number if returning guest
            if 'guest_number' in guest_info:
                info_items.insert(1, ("Guest No:", guest_info.get('guest_number', 'N/A')))
            
            for label, value in info_items:
                row_spacing = max(2, int(self.screen_height * 0.003))
                row = tk.Frame(self.guest_details_frame, bg='#e8f5e9')
                row.pack(fill="x", pady=row_spacing)
                
                label_width = max(12, int(self.screen_width / 70))
                tk.Label(row, text=label, font=("Arial", label_font_size, "bold"), 
                        fg="#333333", bg='#e8f5e9', width=label_width, anchor="w").pack(side="left")
                tk.Label(row, text=value, font=("Arial", value_font_size), 
                        fg="#2e7d32", bg='#e8f5e9').pack(side="left", padx=(8, 0))
            
            # Show the guest info panel with responsive spacing
            panel_spacing_y = max(15, int(self.screen_height * 0.02))
            self.guest_info_panel.pack(fill="x", pady=(panel_spacing_y, 0))
        except Exception as e:
            print(f"Error showing guest info: {e}")

    def show_verification_summary(self, summary_data):
        """Display verification summary with responsive design"""
        try:
            # Clear previous summary
            for widget in self.summary_frame.winfo_children():
                widget.destroy()
            
            # Responsive fonts
            summary_font_size = max(9, int(self.screen_width / 95))
            
            if isinstance(summary_data, dict):
                for key, value in summary_data.items():
                    summary_spacing = max(1, int(self.screen_height * 0.002))
                    summary_row = tk.Frame(self.summary_frame, bg='#f5f5f5')
                    summary_row.pack(fill="x", pady=summary_spacing)
                    
                    tk.Label(summary_row, text=f"{key}:", font=("Arial", summary_font_size, "bold"), 
                            fg="#333333", bg='#f5f5f5', anchor="w").pack(side="left")
                    tk.Label(summary_row, text=str(value), font=("Arial", summary_font_size), 
                            fg="#666666", bg='#f5f5f5').pack(side="left", padx=(6, 0))
            
            # Show the summary panel with responsive spacing
            panel_spacing_y = max(8, int(self.screen_height * 0.01))
            self.summary_panel.pack(fill="x", pady=(panel_spacing_y, 0))
        except Exception as e:
            print(f"Error showing verification summary: {e}")

    def show_final_result(self, result):
        """Show final verification result - Clean & Professional Design (Guest Version)"""
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
                name = result.get('name', 'Visitor')
                if ',' in name:
                    parts = name.split(',')
                    if len(parts) >= 2:
                        name = f"{parts[1].strip()} {parts[0].strip()}"
                
                # Welcome message
                welcome = tk.Label(content, text=f"Welcome, {name}", 
                                 font=("Arial", 20), 
                                 fg="#333333", bg='#FFD700')
                welcome.pack(pady=(0, 15))
                
                # Guest info box (plate number and office)
                info_frame = tk.Frame(content, bg='#E8F5E9', bd=0)
                info_frame.pack(pady=(10, 0), padx=40, fill='x')
                
                plate = result.get('plate_number', 'N/A')
                office = result.get('office', 'N/A')
                
                info_text = f"🚗 Plate: {plate}\n🏢 Visiting: {office}"
                info_label = tk.Label(info_frame, 
                                    text=info_text, 
                                    font=("Arial", 14), 
                                    fg="#1B5E20", bg='#E8F5E9',
                                    pady=12,
                                    justify='center')
                info_label.pack()
                
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
                elif key == 'license_status':
                    self.license_status.set(value)
                elif key == 'current_step':
                    self.current_step.set(value)
                elif key == 'guest_info':
                    self.show_guest_info(value)
                elif key == 'verification_summary':
                    self.show_verification_summary(value)
                elif key == 'final_result':
                    self.show_final_result(value)
                elif key == 'camera_operation_complete':
                    # Restore fullscreen after camera operations
                    self.root.after(500, self.ensure_fullscreen)  # Small delay to ensure camera cleanup
        except Exception as e:
            print(f"Error updating status: {e}")
    
    def start_verification(self):
        """Start verification in separate thread"""
        self.current_step.set("🚀 Initializing visitor verification...")
        
        # Run verification in thread - STORE THE REFERENCE
        self.verification_thread = threading.Thread(target=self.run_verification_thread, daemon=True)
        self.verification_thread.start()
    
    def run_verification_thread(self):
        """Run verification and update GUI - UPDATE THIS FUNCTION"""
        try:
            if not hasattr(self, 'is_running'):
                self.is_running = True
                
            if not self.is_running:
                return
                
            # Call the verification function with callback
            result = self.verification_function(self.update_status_callback)
            
            # CHANGE: Use queue instead of direct GUI updates
            if hasattr(self, 'result_queue') and self.is_running:
                self.result_queue.put(('success', result))
            else:
                # Fallback to old method if queue not available
                if self.root and self.is_running:
                    try:
                        self.root.after(0, lambda: self.update_status({'final_result': result}))
                    except RuntimeError as e:
                        print(f"⚠️ GUI update skipped: {e}")
                        
        except Exception as e:
            print(f"❌ Verification thread error: {e}")
            error_result = {
                'verified': False,
                'reason': f'Error: {str(e)}'
            }
            
            # CHANGE: Use queue for errors too
            if hasattr(self, 'result_queue') and self.is_running:
                self.result_queue.put(('error', error_result))
            else:
                # Fallback to old method
                if self.root and self.is_running:
                    try:
                        self.root.after(0, lambda: self.update_status({'final_result': error_result}))
                    except RuntimeError as e:
                        print(f"⚠️ Error GUI update skipped: {e}")

    def check_verification_result(self):
        """ADD this new function"""
        try:
            if not hasattr(self, 'is_running') or not self.is_running:
                return
                
            # Check for results from verification thread
            try:
                while not self.result_queue.empty():
                    result_type, data = self.result_queue.get_nowait()
                    
                    if result_type == 'success':
                        self.update_status({'final_result': data})
                        # Auto-close after 3 seconds
                        if self.root:
                            self.root.after(3000, self.safe_close)
                    elif result_type == 'error':
                        self.update_status({'final_result': data})
                        # Auto-close after 5 seconds for errors
                        if self.root:
                            self.root.after(5000, self.safe_close)
                            
                    return  # Process one result at a time
            except:
                pass  # No results yet
            
            # Schedule next check if still running
            if self.is_running and self.root:
                self.root.after(100, self.check_verification_result)
                
        except Exception as e:
            print(f"❌ Result check error: {e}")

    def safe_close(self):
        """ADD this new function"""
        try:
            print("🏁 Closing verification GUI...")
            if hasattr(self, 'is_running'):
                self.is_running = False
            
            # Wait for verification thread to finish
            if hasattr(self, 'verification_thread') and self.verification_thread and self.verification_thread.is_alive():
                self.verification_thread.join(timeout=1.0)
            
            # Destroy GUI
            if hasattr(self, 'root') and self.root:
                self.root.quit()
                self.root.destroy()
                
        except Exception as e:
            print(f"❌ Close error: {e}")
    
    def update_status_callback(self, status_dict):
        """Callback for status updates"""
        try:
            self.root.after(0, lambda: self.update_status(status_dict))
        except Exception as e:
            print(f"Error in callback: {e}")
    
    def close(self):
        """Close the GUI - UPDATE THIS FUNCTION"""
        try:
            # ADD: Set running flag to false first
            if hasattr(self, 'is_running'):
                self.is_running = False
                
            self.verification_complete = True
            
            # Wait for verification thread to finish
            if hasattr(self, 'verification_thread') and self.verification_thread and self.verification_thread.is_alive():
                self.verification_thread.join(timeout=1.0)
            
            if hasattr(self, '_update_timer'):
                self.root.after_cancel(self._update_timer)
                
            self.root.quit()
            self.root.destroy()
        except Exception as e:
            print(f"Error closing GUI: {e}")
    
    def run(self):
        """Main GUI loop - UPDATE THIS FUNCTION"""
        try:
            print(f"\n{'='*60}")
            print(f"🎫 Guest Verification GUI Started")
            print(f"📱 Responsive Mode: {self.screen_width}x{self.screen_height}")
            if self.is_square_display:
                print(f"📺 Display Type: Square/4:3 Touch Screen Optimized")
            print(f"{'='*60}")
            
            # ADD: Initialize thread-safe queue and running flag
            self.result_queue = queue.Queue()
            self.is_running = True
            
            # ADD: Start result checker
            self.check_verification_result()
            
            # Handle window close
            self.root.protocol("WM_DELETE_WINDOW", self.safe_close)
            
            # Bind F11 for fullscreen toggle and Ctrl+C for emergency abort
            self.root.bind('<F11>', self.toggle_fullscreen)
            self.root.bind('<Control-c>', self.emergency_abort)
            
            # REMOVE THE DUPLICATE: Don't create another thread here
            # The start_verification() already creates a thread
            # Start verification after GUI loads
            self.root.after(1000, self.start_verification)  # This already creates the thread
            
            # Start GUI loop
            self.root.mainloop()
            
        except KeyboardInterrupt:
            print("\n🛑 Verification interrupted by user")
            self.safe_close()
        except Exception as e:
            print(f"❌ GUI error: {e}")
            self.safe_close()
        finally:
            if hasattr(self, 'is_running'):
                self.is_running = False
