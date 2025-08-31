# main_window.py
import tkinter as tk
from tkinter import messagebox
import os
import sys
import subprocess
import sqlite3
from PIL import Image, ImageTk
from datetime import datetime
import threading
import time

from etc.controllers.vip import (
    authenticate_admin_for_vip,
    determine_vip_action,
    process_vip_time_in,
    process_vip_time_out,
    validate_vip_plate_format
)

from database.vip_operations import get_vip_stats

class MotorPassGUI:
    def __init__(self, system_name, system_version, admin_function, student_function, guest_function):
        self.system_name = system_name
        self.system_version = system_version
        self.admin_function = admin_function
        self.student_function = student_function
        self.guest_function = guest_function
        
        # ADD ONLY THIS LINE - restart tracking
        self._restart_needed = False
        
        self.root = tk.Tk()
        self.root.title(f"{system_name} System v{system_version}")
        
        # Responsive window sizing - auto-detect screen size and aspect ratio
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        
        # Calculate aspect ratio to determine display type
        aspect_ratio = self.screen_width / self.screen_height
        self.is_square_display = abs(aspect_ratio - 1.0) < 0.2  # Within 20% of square
        self.is_wide_display = aspect_ratio > 1.5  # Wider than 3:2
        
        # Set base size for calculations
        if self.is_square_display:
            self.display_size = min(self.screen_width, self.screen_height)
        else:
            self.display_size = min(self.screen_width, self.screen_height)
            
        self.root.geometry(f"{self.screen_width}x{self.screen_height}")
        self.root.resizable(False, False)
        self.root.configure(bg='black')
        
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
        self.root.bind('<Escape>', self.toggle_fullscreen)
        # Also bind F11 for fullscreen toggle
        self.root.bind('<F11>', self.toggle_fullscreen)
        
        self.setup_window()
        self.start_clock()
        self.start_time_in_counter()
        
    def toggle_fullscreen(self, event=None):
        """Toggle fullscreen mode - useful for admin access or testing"""
        try:
            current_state = self.root.attributes('-fullscreen')
            self.root.attributes('-fullscreen', not current_state)
            
            if current_state:
                # Exiting fullscreen
                print("Exited fullscreen mode (Taskbar visible)")
            else:
                # Entering fullscreen  
                print("Entered fullscreen mode (Taskbar hidden)")
                
        except Exception as e:
            print(f"Error toggling fullscreen: {e}")

    def setup_window(self):
        """Setup main window"""
        self.center_window()
        self.setup_background()
        self.create_header()
        self.create_clock()
        self.create_time_in_counter()
        self.create_selection_interface()
        
    def center_window(self):
        """Center window on screen"""
        self.root.update_idletasks()
        
    def setup_background(self):
        """Setup responsive fullscreen background image"""
        # Try to load the background image
        background_paths = [
            "assets/background.jpg",
            "assets/background.png",
            "background.jpg",
            "background.png"
        ]
        
        background_loaded = False
        for bg_path in background_paths:
            if os.path.exists(bg_path):
                try:
                    image = Image.open(bg_path)
                    # Resize to fill screen completely while maintaining aspect ratio
                    image_ratio = image.width / image.height
                    screen_ratio = self.screen_width / self.screen_height
                    
                    if image_ratio > screen_ratio:
                        # Image is wider than screen
                        new_height = self.screen_height
                        new_width = int(new_height * image_ratio)
                    else:
                        # Image is taller than screen
                        new_width = self.screen_width
                        new_height = int(new_width / image_ratio)
                    
                    image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    self.background_image = ImageTk.PhotoImage(image)
                    
                    # Create background label that fills entire screen
                    background_label = tk.Label(self.root, image=self.background_image)
                    background_label.place(x=(self.screen_width - new_width)//2, 
                                         y=(self.screen_height - new_height)//2,
                                         width=new_width, height=new_height)
                    background_loaded = True
                    break
                except Exception as e:
                    print(f"Could not load background {bg_path}: {e}")
                    continue
        
        if not background_loaded:
            # Create a gradient background as fallback
            self.create_gradient_background()
    
    def create_gradient_background(self):
        """Create responsive gradient background as fallback"""
        canvas = tk.Canvas(self.root, highlightthickness=0)
        canvas.place(x=0, y=0, width=self.screen_width, height=self.screen_height)
        
        for i in range(self.screen_height):
            # Create a brown to darker brown gradient
            intensity = int(139 - (i / self.screen_height) * 50)  # From 139 to 89
            color = f"#{intensity:02x}{int(intensity*0.6):02x}{int(intensity*0.4):02x}"
            canvas.create_line(0, i, self.screen_width, i, fill=color)
    
    def create_header(self):
        """Create responsive header with logo and title"""
        # Calculate responsive header height based on screen size
        header_height = max(100, int(self.screen_height * 0.12))
        
        # Header overlay with transparency effect
        header_frame = tk.Frame(self.root, bg='#46230a', height=header_height)
        header_frame.pack(fill="x", padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        # Logo and title container
        content_frame = tk.Frame(header_frame, bg='#46230a')
        content_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Calculate responsive logo size
        logo_size = max(60, int(header_height * 0.7))
        
        # Logo section
        logo_frame = tk.Frame(content_frame, bg='#46230a', width=logo_size, height=logo_size)
        logo_frame.pack(side="left", padx=(0, 15), pady=5)
        logo_frame.pack_propagate(False)
        
        # Try to load logo
        logo_loaded = False
        logo_paths = ["assets/logo.png", "logo.png", "../assets/logo.png"]
        
        for logo_path in logo_paths:
            if os.path.exists(logo_path):
                try:
                    logo_img = Image.open(logo_path)
                    logo_img = logo_img.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
                    self.logo_image = ImageTk.PhotoImage(logo_img)
                    logo_label = tk.Label(logo_frame, image=self.logo_image, bg='#46230a')
                    logo_label.pack(expand=True)
                    logo_loaded = True
                    break
                except Exception as e:
                    print(f"Could not load logo {logo_path}: {e}")
                    continue
        
        if not logo_loaded:
            # Fallback logo with responsive sizing
            fallback_size = int(logo_size * 0.8)
            logo_bg = tk.Frame(logo_frame, bg='#DAA520', width=fallback_size, height=fallback_size)
            logo_bg.pack(expand=True)
            logo_bg.pack_propagate(False)
            logo_text = tk.Label(logo_bg, text="🚗", font=("Arial", int(logo_size*0.5)), bg='#DAA520', fg='#2F1B14')
            logo_text.place(relx=0.5, rely=0.5, anchor="center")
        
        # Title section
        title_frame = tk.Frame(content_frame, bg='#46230a')
        title_frame.pack(side="left", fill="y", padx=(15, 0))
        
        # Responsive font sizes
        title_font_size = max(20, int(self.screen_width / 45))
        subtitle_font_size = max(9, int(self.screen_width / 120))
        
        # Main title with responsive typography
        title_label = tk.Label(title_frame, text=self.system_name, 
                              font=("Arial", title_font_size, "bold"), fg="#DAA520", bg='#46230a')
        title_label.pack(anchor="w", pady=(10, 0))
        
        # Subtitle
        subtitle_label = tk.Label(title_frame, text=f"**We secure the safeness of your motorcycle in side our campus**", 
                                 font=("Arial", subtitle_font_size), fg="#c7971d", bg='#46230a')
        subtitle_label.pack(anchor="w")

    def create_clock(self):
        """Create responsive digital clock display in top right corner"""
        # Calculate responsive clock dimensions
        clock_width = max(180, int(self.screen_width * 0.15))
        clock_height = max(70, int(self.screen_height * 0.08))
        
        # Clock container in top right with responsive positioning
        self.clock_frame = tk.Frame(self.root, bg='#46230a', bd=2, relief='solid')
        margin = max(10, int(self.screen_width * 0.01))
        self.clock_frame.place(x=self.screen_width - clock_width - margin, 
                              y=margin, 
                              width=clock_width, height=clock_height)
        
        # Responsive font sizes
        time_font_size = max(16, int(self.screen_width / 70))
        date_font_size = max(8, int(self.screen_width / 140))
        
        # Time display
        self.time_label = tk.Label(self.clock_frame, text="00:00:00", 
                                  font=("Arial", time_font_size, "bold"), fg="#DAA520", bg='#46230a')
        self.time_label.pack(pady=(5, 0))
        
        # Date display
        self.date_label = tk.Label(self.clock_frame, text="Monday, January 01, 2025", 
                                  font=("Arial", date_font_size), fg="#FFFFFF", bg='#46230a')
        self.date_label.pack()
    
    def create_time_in_counter(self):
        """Create responsive unified counter display with VIP and regular counters"""
        # Calculate responsive counter dimensions
        counter_width = max(150, int(self.screen_width * 0.12))
        counter_height = max(120, int(self.screen_height * 0.15))
        
        # Counter container in bottom left with responsive positioning (moved up)
        margin = max(10, int(self.screen_width * 0.01))
        bottom_margin = max(30, int(self.screen_height * 0.04))  # Increased bottom margin
        self.counter_frame = tk.Frame(self.root, bg='#46230a', bd=2, relief='solid')
        self.counter_frame.place(x=margin, 
                                y=self.screen_height - counter_height - bottom_margin, 
                                width=counter_width, height=counter_height)
        
        # Responsive font sizes
        title_font_size = max(10, int(self.screen_width / 120))
        count_font_size = max(18, int(self.screen_width / 60))
        label_font_size = max(8, int(self.screen_width / 150))
        
        # Regular counter
        tk.Label(self.counter_frame, text="CURRENT INSIDE", 
                font=("Arial", title_font_size, "bold"), fg="#DAA520", bg='#46230a').pack(pady=(5, 0))
        
        self.count_label = tk.Label(self.counter_frame, text="0", 
                                   font=("Arial", count_font_size, "bold"), fg="#FFFFFF", bg='#46230a')
        self.count_label.pack()
        
        tk.Label(self.counter_frame, text="Students/Staff", 
                font=("Arial", label_font_size), fg="#c7971d", bg='#46230a').pack()
        
        # Separator
        separator = tk.Frame(self.counter_frame, bg='#DAA520', height=1)
        separator.pack(fill="x", padx=10, pady=2)
        
        # VIP counter
        self.vip_count_label = tk.Label(self.counter_frame, text="0", 
                                       font=("Arial", int(count_font_size*0.8), "bold"), fg="#FF4444", bg='#46230a')
        self.vip_count_label.pack()
        
        tk.Label(self.counter_frame, text="VIPs Inside", 
                font=("Arial", label_font_size), fg="#c7971d", bg='#46230a').pack()

    def create_selection_interface(self):
        """Create responsive centered selection interface that adapts to screen aspect ratio"""
        # Calculate responsive overlay dimensions based on screen type
        if self.is_square_display:
            # Square display (like your touch screen)
            overlay_width = max(450, int(self.screen_width * 0.35))
            overlay_height = max(400, int(self.screen_height * 0.45))
        
        elif self.is_wide_display:
            # Wide display (16:9, 21:9, etc.)
            overlay_width = max(450, int(self.screen_width * 0.35))
            overlay_height = max(400, int(self.screen_height * 0.45))
        
        else:
            # Standard display - balanced approach (wider and taller)
            overlay_width = max(450, int(self.screen_width * 0.35))
            overlay_height = max(400, int(self.screen_height * 0.45))
        
        
        # Ensure minimum size for touch interaction
        overlay_width = max(overlay_width, 500)
        overlay_height = max(overlay_height, 450)
        
        # Create shadow effect (multiple layers for depth)
        shadow_offsets = [(6, 6, '#404040'), (4, 4, '#505050'), (2, 2, '#606060')]
        for offset_x, offset_y, shadow_color in shadow_offsets:
            shadow_frame = tk.Frame(self.root, bg=shadow_color)
            shadow_frame.place(relx=0.5, rely=0.5,  # Moved up from 0.5 to 0.47
                             width=overlay_width, height=overlay_height, 
                             anchor='center', x=offset_x, y=offset_y)
        
        # Main container with glass morphism effect - MOVED SLIGHTLY UP
        self.main_overlay = tk.Frame(self.root, bg='#2c1810', bd=0, relief='flat')
        self.main_overlay.place(relx=0.5, rely=0.5,  # Moved up from 0.5 to 0.47
                               width=overlay_width, height=overlay_height, 
                               anchor='center')
        
        # Add border effect
        border_frame = tk.Frame(self.main_overlay, bg='#D4AF37', height=3)
        border_frame.pack(fill="x", side="top")
        
        # Inner container with padding
        inner_container = tk.Frame(self.main_overlay, bg='#2c1810')
        inner_container.pack(fill="both", expand=True, padx=3, pady=3)
        
        # Calculate responsive font sizes based on display type
        if self.is_square_display:
            # Square display - original sizing
            title_font_size = max(18, int(self.screen_width / 60))
            subtitle_font_size = max(8, int(self.screen_width / 140))
            button_font_size = max(12, int(self.screen_width / 90))
        elif self.is_wide_display:
            # Wide display - use height for better proportion
            title_font_size = max(20, int(self.screen_height / 35))
            subtitle_font_size = max(9, int(self.screen_height / 80))
            button_font_size = max(13, int(self.screen_height / 55))
        else:
            # Standard display - balanced approach
            base_size = min(self.screen_width, self.screen_height)
            title_font_size = max(19, int(base_size / 50))
            subtitle_font_size = max(9, int(base_size / 90))
            button_font_size = max(13, int(base_size / 70))
        
        # Title section with enhanced styling
        title_height = max(80, int(overlay_height * 0.2))
        title_container = tk.Frame(inner_container, bg='#3d2317', height=title_height)
        title_container.pack(fill="x", padx=15, pady=(15, 0))
        title_container.pack_propagate(False)
        
        # Decorative line above title
        deco_line = tk.Frame(title_container, bg='#D4AF37', height=2)
        deco_line.pack(fill="x", pady=(10, 5))
        
        title_label = tk.Label(title_container, text="YOU ARE A:", 
                              font=("Arial", title_font_size, "bold"), fg="#F5DEB3", bg='#3d2317')
        title_label.pack(expand=True)
        
        # Subtitle for better context
        subtitle_label = tk.Label(title_container, text="Please select your access level", 
                                 font=("Arial", subtitle_font_size), fg="#D4AF37", bg='#3d2317')
        subtitle_label.pack(pady=(0, 10))
        
        # Buttons container with enhanced styling
        buttons_frame = tk.Frame(inner_container, bg='#2c1810')
        buttons_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Create user type buttons with adaptive sizing
        if self.is_square_display:
            button_height = max(50, int(overlay_height * 0.12))
        elif self.is_wide_display:
            button_height = max(55, int(overlay_height * 0.10))  # Slightly shorter for wide screens
        else:
            button_height = max(52, int(overlay_height * 0.11))
            
        self.create_enhanced_button(buttons_frame, "👨‍🎓 STUDENT/STAFF", self.student_staff_clicked, "#D4AF37", "#8B7355", button_height, button_font_size)
        self.create_enhanced_button(buttons_frame, "👤 VISITOR", self.guest_clicked, "#D4AF37", "#8B7355", button_height, button_font_size)
        self.create_enhanced_button(buttons_frame, "⚙️ ADMIN", self.admin_clicked, "#CD853F", "#A0522D", button_height, button_font_size)
        
        # Separator line
        separator = tk.Frame(buttons_frame, bg='#5c3e28', height=1)
        separator.pack(fill="x", pady=15)
        
        # Exit button with enhanced styling
        exit_height = max(45, int(overlay_height * 0.1))
        exit_frame = tk.Frame(buttons_frame, bg='#2c1810', height=exit_height)
        exit_frame.pack(fill="x", pady=(5, 10))
        exit_frame.pack_propagate(False)
        
        exit_btn = tk.Button(exit_frame, text="🚪 EXIT SYSTEM", 
                           font=("Arial", button_font_size, "bold"), bg="#8B4513", fg="#F5DEB3",
                           bd=0, cursor="hand2", command=self.exit_system, 
                           relief='flat', activebackground="#A0522D", activeforeground="white")
        exit_btn.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Enhanced hover effects for exit button
        def exit_on_enter(e):
            exit_btn.config(bg="#A0522D", relief='raised', bd=1)
        def exit_on_leave(e):
            exit_btn.config(bg="#8B4513", relief='flat', bd=0)
        
        exit_btn.bind("<Enter>", exit_on_enter)
        exit_btn.bind("<Leave>", exit_on_leave)
        
        # Bring overlay to front
        self.main_overlay.lift()
        self.create_vip_button()
        
    def create_enhanced_button(self, parent, text, command, primary_color, secondary_color, button_height, font_size):
        """Create responsive enhanced styled button with advanced hover effects and icons"""
        btn_frame = tk.Frame(parent, bg='#2c1810', height=button_height)
        btn_frame.pack(fill="x", pady=8)
        btn_frame.pack_propagate(False)
        
        # Button container for 3D effect
        btn_container = tk.Frame(btn_frame, bg=secondary_color, bd=0)
        btn_container.pack(fill="both", expand=True, padx=8, pady=3)
        
        # Main button
        btn = tk.Button(btn_container, text=text, font=("Arial", font_size, "bold"),
                       bg=primary_color, fg="#2F1B14", bd=0, cursor="hand2",
                       command=command, relief='flat', 
                       activebackground="#F0E68C", activeforeground="#2F1B14",
                       padx=20, pady=15)
        btn.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Advanced hover effects with smooth transitions
        def on_enter(e):
            btn.config(bg="#F0E68C", relief='raised', bd=1)
            btn_container.config(bg="#B8860B")
            # Add subtle scaling effect
            btn.config(font=("Arial", font_size + 1, "bold"))
            
        def on_leave(e):
            btn.config(bg=primary_color, relief='flat', bd=0)
            btn_container.config(bg=secondary_color)
            btn.config(font=("Arial", font_size, "bold"))
            
        def on_click(e):
            btn.config(bg="#DAA520", relief='sunken')
            parent.after(100, lambda: btn.config(relief='flat'))
            
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        btn.bind("<Button-1>", on_click)

    def create_vip_button(self):
        """Create responsive VIP button in bottom right corner"""
        # Calculate responsive VIP button dimensions
        vip_width = max(100, int(self.screen_width * 0.08))
        vip_height = max(80, int(self.screen_height * 0.08))
        
        # Position in bottom right with responsive margin (moved up)
        margin = max(10, int(self.screen_width * 0.01))
        bottom_margin = max(30, int(self.screen_height * 0.04))  # Increased bottom margin
        
        # VIP button frame
        self.vip_frame = tk.Frame(self.root, bg="#FF4444", bd=3, relief='raised')
        self.vip_frame.place(x=self.screen_width - vip_width - margin, 
                            y=self.screen_height - vip_height - bottom_margin, 
                            width=vip_width, height=vip_height)
        
        # Responsive font size
        vip_font_size = max(8, int(self.screen_width / 140))
        
        # VIP button
        vip_btn = tk.Button(self.vip_frame, text="🌟\nVIP", 
                          font=("Arial", vip_font_size, "bold"),
                          bg="#FF4444", fg="white", bd=0, cursor="hand2",
                          command=self.handle_vip_access, relief='flat',
                          activebackground="#FF6666", activeforeground="white")
        vip_btn.pack(fill="both", expand=True)
        
        # VIP button hover effects
        def vip_on_enter(e):
            vip_btn.config(bg="#FF6666", relief='raised')
            self.vip_frame.config(bg="#FF6666")
            
        def vip_on_leave(e):
            vip_btn.config(bg="#FF4444", relief='flat')
            self.vip_frame.config(bg="#FF4444")
            
        vip_btn.bind("<Enter>", vip_on_enter)
        vip_btn.bind("<Leave>", vip_on_leave)

    # Keep all other methods unchanged
    def get_current_time_in_count(self):
        """Get count of people currently timed in"""
        try:
            # Connect to database
            conn = sqlite3.connect('database/motorpass.db')
            cursor = conn.cursor()
            
            # Count people who are currently timed in (status = 'IN')
            cursor.execute("""
                SELECT COUNT(*) FROM current_status 
                WHERE status = 'IN'
            """)
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except Exception as e:
            print(f"Error getting time-in count: {e}")
            return 0

    def get_current_vip_count(self):
        """Get count of VIPs currently timed in"""
        try:
            stats = get_vip_stats()
            return stats['current_in']
        except Exception as e:
            print(f"Error getting VIP count: {e}")
            return 0

    def start_time_in_counter(self):
        """Start the time-in counter update thread (includes VIP counter)"""
        def update_counters():
            while True:
                try:
                    # Update regular counter
                    count = self.get_current_time_in_count()
                    self.count_label.config(text=str(count))
                    
                    # Update VIP counter
                    vip_count = self.get_current_vip_count()
                    self.vip_count_label.config(text=str(vip_count))
                    
                    time.sleep(5)  # Update every 5 seconds
                except:
                    break
        
        counter_thread = threading.Thread(target=update_counters, daemon=True)
        counter_thread.start()
        
    def start_clock(self):
        """Start the clock update thread"""
        def update_clock():
            while True:
                try:
                    now = datetime.now()
                    time_str = now.strftime("%H:%M:%S")
                    date_str = now.strftime("%A, %B %d, %Y")
                    
                    self.time_label.config(text=time_str)
                    self.date_label.config(text=date_str)
                    
                    time.sleep(1)
                except:
                    break
        
        clock_thread = threading.Thread(target=update_clock, daemon=True)
        clock_thread.start()

    def handle_vip_access(self):
        """Handle VIP access button click with authentication"""
        # First authenticate admin
        if not authenticate_admin_for_vip():
            return
            
        vip_window = tk.Toplevel(self.root)
        vip_window.title("VIP Access")
        vip_window.geometry("450x550")
        vip_window.configure(bg="white")
        vip_window.resizable(False, False)
        
        # Center the window
        vip_window.update_idletasks()
        x = (vip_window.winfo_screenwidth() // 2) - 225
        y = (vip_window.winfo_screenheight() // 2) - 275
        vip_window.geometry(f"450x550+{x}+{y}")
        
        vip_window.transient(self.root)
        vip_window.grab_set()
        
        # Header
        header_frame = tk.Frame(vip_window, bg="#FF4444", height=80)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="VIP ACCESS", 
                font=("Arial", 20, "bold"), fg="white", bg="#FF4444").pack(expand=True)
        
        # Main form frame
        form_frame = tk.Frame(vip_window, bg="white")
        form_frame.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Instructions
        instructions = tk.Label(form_frame, 
                               text="Enter plate number - System will automatically\ndetermine TIME IN or TIME OUT",
                               font=("Arial", 11), 
                               fg="#666666", bg="white",
                               justify="center")
        instructions.pack(pady=(0, 20))
        
        # Plate Number Input
        tk.Label(form_frame, text="Plate Number:", 
                font=("Arial", 12, "bold"), bg="white", fg="#34495E").pack(anchor="w", pady=(0,5))
        
        plate_entry = tk.Entry(form_frame, font=("Arial", 14), 
                              width=25, justify="center")
        plate_entry.pack(pady=(0, 10), fill="x")
        plate_entry.focus_set()
        
        # Status display
        status_label = tk.Label(form_frame, text="Enter plate number to check status", 
                               font=("Arial", 11), fg="#7F8C8D", bg="white",
                               wraplength=350, justify="center")
        status_label.pack(pady=(0, 20))
        
        # Purpose selection frame (hidden initially)
        purpose_frame = tk.Frame(form_frame, bg="white")
        purpose_var = tk.StringVar()
        purpose_buttons = []
        
        tk.Label(purpose_frame, text="Select Purpose:", 
                font=("Arial", 11, "bold"), bg="white", fg="#34495E").pack(anchor="w", pady=(0,10))
        
        # Create a sub-frame for the button grid to avoid geometry manager conflict
        buttons_grid_frame = tk.Frame(purpose_frame, bg="white")
        buttons_grid_frame.pack(fill="x")
        
        purposes = ["Meeting", "Delivery", "Maintenance", "Inspection", "Other"]
        for i, purpose in enumerate(purposes):
            btn = tk.Button(buttons_grid_frame, text=purpose, font=("Arial", 9),
                           bg="#f0f0f0", fg="black", bd=1, relief='solid',
                           width=12, cursor="hand2")
            btn.grid(row=i//3, column=i%3, padx=3, pady=3, sticky="ew")
            purpose_buttons.append(btn)
            
            def select_purpose(p=purpose, b=btn):
                purpose_var.set(p)
                for button in purpose_buttons:
                    button.config(bg="#f0f0f0", fg="black")
                b.config(bg="#27AE60", fg="white")
            
            btn.config(command=select_purpose)
        
        # Configure grid weights for the buttons_grid_frame
        for i in range(3):
            buttons_grid_frame.grid_columnconfigure(i, weight=1)
        
        def check_plate_status():
            plate_number = plate_entry.get().strip().upper()
            if not plate_number:
                status_label.config(text="Enter plate number to check status", fg="#7F8C8D")
                purpose_frame.pack_forget()
                return
            
            # Validate plate format
            is_valid, validation_msg = validate_vip_plate_format(plate_number)
            if not is_valid:
                status_label.config(text=f"Invalid: {validation_msg}", fg="#E74C3C")
                purpose_frame.pack_forget()
                return
            
            # Determine action
            action_result = determine_vip_action(plate_number)
            
            if action_result['action'] == 'TIME_IN':
                status_label.config(text="TIME IN - Select purpose below", fg="#27AE60")
                purpose_frame.pack(fill="x", pady=10)
                purpose_var.set("")  # Reset purpose
                # Reset button colors
                for btn in purpose_buttons:
                    btn.config(bg="#f0f0f0", fg="black")
            elif action_result['action'] == 'TIME_OUT':
                vip_info = action_result['vip_info']
                status_label.config(text=f"TIME OUT - {vip_info['purpose']}", fg="#E74C3C")
                purpose_frame.pack_forget()
            else:
                status_label.config(text=f"Error: {action_result['message']}", fg="#E74C3C")
                purpose_frame.pack_forget()
        
        # Bind plate entry to check status
        plate_entry.bind('<KeyRelease>', lambda e: check_plate_status())
        
        # Buttons frame
        button_frame = tk.Frame(form_frame, bg="white")
        button_frame.pack(side="bottom", fill="x", pady=(30,0))
        
        def cancel_vip():
            vip_window.destroy()
        
        def submit_vip():
            plate_number = plate_entry.get().strip().upper()
            
            if not plate_number:
                messagebox.showerror("Error", "Please enter plate number!")
                return
            
            # Validate plate format
            is_valid, validation_msg = validate_vip_plate_format(plate_number)
            if not is_valid:
                messagebox.showerror("Invalid Plate", validation_msg)
                return
            
            # Determine action
            action_result = determine_vip_action(plate_number)
            
            if action_result['action'] == 'TIME_IN':
                purpose = purpose_var.get()
                if not purpose:
                    messagebox.showerror("Error", "Please select purpose for TIME IN!")
                    return
                
                # Process TIME IN
                result = process_vip_time_in(plate_number, purpose)
                if result['success']:
                    messagebox.showinfo("Success", f"VIP TIME IN successful!\nPlate: {plate_number}\nPurpose: {purpose}")
                    vip_window.destroy()
                else:
                    messagebox.showerror("Error", f"TIME IN failed: {result['message']}")
                    
            elif action_result['action'] == 'TIME_OUT':
                # Process TIME OUT
                result = process_vip_time_out(plate_number)
                if result['success']:
                    vip_info = action_result['vip_info']
                    messagebox.showinfo("Success", f"VIP TIME OUT successful!\nPlate: {plate_number}\nPurpose: {vip_info['purpose']}")
                    vip_window.destroy()
                else:
                    messagebox.showerror("Error", f"TIME OUT failed: {result['message']}")
            else:
                messagebox.showerror("Error", f"{action_result['message']}")
        
        # Cancel and Submit buttons
        tk.Button(button_frame, text="Cancel", font=("Arial", 11, "bold"),
                 bg="#95a5a6", fg="white", cursor="hand2",
                 command=cancel_vip, width=12, pady=8).pack(side="left", padx=(0,10))
        
        tk.Button(button_frame, text="Submit", font=("Arial", 11, "bold"),
                 bg="#27AE60", fg="white", cursor="hand2",
                 command=submit_vip, width=12, pady=8).pack(side="right")

    def run_function_with_window(self, function, title):
        """Run function with main window reference passed (backwards compatible)"""
        try:
            print(f"\n{'='*50}")
            print(f"🚀 {title} Started")
            print(f"{'='*50}")
            
            # Check if function accepts main_window parameter
            import inspect
            sig = inspect.signature(function)
            
            if 'main_window' in sig.parameters:
                # Function expects main_window parameter
                function(main_window=self.root)
            else:
                # Function doesn't expect main_window parameter (backwards compatibility)
                function()
            
            print(f"\n✅ {title} completed")
            
        except Exception as e:
            print(f"❌ Error in {title}: {e}")
            messagebox.showerror("Error", f"An error occurred in {title}:\n\n{str(e)}")

    def student_staff_clicked(self):
        """Handle Student/Staff button click"""
        self.run_function_with_window(self.student_function, "Student/Staff Verification")

    def guest_clicked(self):
        """Handle Visitor button click"""
        self.run_function_with_window(self.guest_function, "Visitor Verification")

    def admin_clicked(self):
        """Handle Admin button click"""
        self.run_function_with_window(self.admin_function, "Admin Panel")

    def exit_system(self):
        """Handle system exit"""
        if messagebox.askyesno("Exit System", "Are you sure you want to exit MotorPass system?"):
            print("\n" + "="*50)
            print("🏁 MotorPass System Shutdown")
            print("="*50)
            self.root.quit()
            self.root.destroy()
            sys.exit()

    def run(self):
        """Run the main GUI"""
        print(f"\n{'='*60}")
        print(f"🚀 {self.system_name} System v{self.system_version} Started")
        print(f"📱 Responsive Mode: {self.screen_width}x{self.screen_height}")
        print(f"{'='*60}")
        
        # Handle window closing
        self.root.protocol("WM_DELETE_WINDOW", self.exit_system)
        
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("\n⚠️  System interrupted by user")
            self.exit_system()
        except Exception as e:
            print(f"\n❌ System error: {e}")
            messagebox.showerror("System Error", f"A critical error occurred:\n\n{str(e)}")
            self.exit_system()
