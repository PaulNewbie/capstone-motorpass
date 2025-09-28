# ui/components/verification_components.py - TRULY reusable components for ANY verification GUI

import tkinter as tk
import os
from PIL import Image, ImageTk

class VerificationUIComponents:
    """Reusable verification UI components that can be used by StudentGUI, GuestGUI, etc."""
    
    @staticmethod
    def create_status_panel(parent, status_vars, screen_info, title="VERIFICATION STATUS"):
        """
        Create reusable status panel that ANY verification GUI can use
        
        Args:
            parent: Parent widget
            status_vars: Dict of status StringVars (can be any number of them)
            screen_info: Screen dimensions info
            title: Panel title (customizable)
        
        Returns:
            Dict with panel reference and status widgets
        """
        screen_width = screen_info['screen_width']
        screen_height = screen_info['screen_height']
        
        # Container
        status_container = tk.Frame(parent, bg='white', relief='raised', bd=3)
        status_container.pack(fill="both", expand=True)
        
        # Title
        title_font_size = max(16, int(screen_width / 50))
        title_padding_y = max(15, int(screen_height * 0.02))
        
        tk.Label(status_container, text=title, 
                font=("Arial", title_font_size, "bold"), fg="#333333", bg='white').pack(pady=title_padding_y)
        
        # Status items container
        status_padding_x = max(20, int(screen_width * 0.02))
        status_padding_y = max(15, int(screen_height * 0.02))
        
        status_items_frame = tk.Frame(status_container, bg='white')
        status_items_frame.pack(fill="x", padx=status_padding_x, pady=(0, status_padding_y))
        
        # Create status items dynamically based on what's passed in
        status_widgets = {}
        row = 0
        for status_key, (label_text, status_var) in status_vars.items():
            widgets = VerificationUIComponents._create_status_item(
                status_items_frame, label_text, status_var, row, screen_info
            )
            status_widgets[status_key] = widgets
            row += 1
        
        return {
            'container': status_container,
            'items_frame': status_items_frame,
            'status_widgets': status_widgets
        }
    
    @staticmethod
    def _create_status_item(parent, label_text, status_var, row, screen_info):
        """Create individual status item - reusable for any verification type"""
        screen_width = screen_info['screen_width']
        screen_height = screen_info['screen_height']
        
        item_spacing_y = max(12, int(screen_height * 0.015))
        item_frame = tk.Frame(parent, bg='white')
        item_frame.pack(fill="x", pady=item_spacing_y)
        
        # Label
        label_font_size = max(12, int(screen_width / 70))
        label = tk.Label(item_frame, text=label_text, font=("Arial", label_font_size, "bold"), 
                        fg="#333333", bg='white')
        label.pack(side="left")
        
        # Status badge
        badge_font_size = max(10, int(screen_width / 85))
        badge_padding_x = max(15, int(screen_width * 0.015))
        badge_padding_y = max(6, int(screen_height * 0.008))
        
        badge = tk.Label(item_frame, text="PENDING", font=("Arial", badge_font_size, "bold"), 
                        fg="#FFFFFF", bg="#95a5a6", padx=badge_padding_x, pady=badge_padding_y, relief='flat')
        badge.pack(side="right", padx=(0, max(8, int(screen_width * 0.008))))
        
        # Status icon
        icon_font_size = max(14, int(screen_width / 60))
        icon_spacing = max(12, int(screen_width * 0.012))
        
        icon_label = tk.Label(item_frame, text="⏸", font=("Arial", icon_font_size), 
                             fg="#95a5a6", bg='white')
        icon_label.pack(side="right", padx=(0, icon_spacing))
        
        # Auto-update when status changes
        status_var.trace_add("write", lambda *args: VerificationUIComponents.update_status_display(
            badge, icon_label, status_var.get()
        ))
        
        return {
            'item_frame': item_frame,
            'label': label,
            'badge': badge,
            'icon': icon_label
        }
    
    @staticmethod
    def update_status_display(badge, icon, status):
        """Update status display - reusable for any verification GUI"""
        status_configs = {
            "VERIFIED": ("#27ae60", "✅", "#27ae60"),
            "FAILED": ("#e74c3c", "❌", "#e74c3c"),
            "CHECKING": ("#f39c12", "🔄", "#f39c12"),
            "PENDING": ("#95a5a6", "⏸", "#95a5a6"),
            "TIMEOUT": ("#e67e22", "⏰", "#e67e22"),
            "ERROR": ("#c0392b", "⚠️", "#c0392b")
        }
        
        if status in status_configs:
            bg_color, icon_text, icon_color = status_configs[status]
            badge.config(text=status, bg=bg_color)
            icon.config(text=icon_text, fg=icon_color)
    
    @staticmethod
    def create_camera_feed_panel(parent, screen_info, title="CAMERA FEED"):
        """Create reusable camera feed panel for any verification GUI"""
        screen_width = screen_info['screen_width']
        screen_height = screen_info['screen_height']
        
        camera_container = tk.Frame(parent, bg='white', relief='raised', bd=3)
        camera_container.pack(fill="both", expand=True)
        
        # Title
        title_font_size = max(16, int(screen_width / 50))
        title_padding_y = max(15, int(screen_height * 0.02))
        
        tk.Label(camera_container, text=title, 
                font=("Arial", title_font_size, "bold"), fg="#333333", bg='white').pack(pady=title_padding_y)
        
        # Camera placeholder
        camera_placeholder = tk.Frame(camera_container, bg='#2c3e50', relief='sunken', bd=2)
        placeholder_padding = max(20, int(min(screen_width, screen_height) * 0.03))
        camera_placeholder.pack(fill="both", expand=True, padx=placeholder_padding, pady=(0, placeholder_padding))
        
        # Camera icon and text
        icon_font_size = max(48, int(min(screen_width, screen_height) / 15))
        text_font_size = max(14, int(screen_width / 60))
        
        tk.Label(camera_placeholder, text="📹", font=("Arial", icon_font_size), 
                fg="#ecf0f1", bg='#2c3e50').pack(expand=True)
        tk.Label(camera_placeholder, text="Camera feed will appear here", 
                font=("Arial", text_font_size), fg="#bdc3c7", bg='#2c3e50').pack(expand=True)
        
        return camera_container
    
    @staticmethod
    def create_motorpass_header(parent, screen_info, time_string, date_string, 
                               subtitle="Verification System", bg_color='#46230a'):
        """Create reusable MotorPass header for any verification GUI"""
        screen_width = screen_info['screen_width']
        screen_height = screen_info['screen_height']
        
        header_height = max(80, int(screen_height * 0.11))
        header = tk.Frame(parent, bg=bg_color, height=header_height)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        header_padding = max(15, int(screen_width * 0.015))
        header_content = tk.Frame(header, bg=bg_color)
        header_content.pack(fill="both", expand=True, padx=header_padding, 
                           pady=max(8, int(header_height * 0.1)))
        
        # Logo section
        VerificationUIComponents._add_logo_section(header_content, header_height, screen_width, bg_color)
        
        # Title section
        title_container = tk.Frame(header_content, bg=bg_color)
        title_container.pack(fill="x", expand=True)
        
        main_title_font = max(18, int(header_height * 0.3))
        tk.Label(title_container, text="MOTORPASS", 
                font=("Arial", main_title_font, "bold"), fg="#FFFFFF", bg=bg_color).pack(anchor="w")
        
        subtitle_font = max(12, int(header_height * 0.18))
        tk.Label(title_container, text=subtitle, 
                font=("Arial", subtitle_font), fg="#FFFFFF", bg=bg_color).pack(anchor="w")

        # Time section  
        VerificationUIComponents._add_time_section(header_content, header_height, time_string, date_string, bg_color)
        
        return header
    
    @staticmethod
    def _add_logo_section(header_content, header_height, screen_width, bg_color):
        """Add logo section - reusable"""
        logo_size = max(60, int(header_height * 0.75))
        logo_container = tk.Frame(header_content, bg=bg_color)
        logo_container.pack(side="left", padx=(0, max(12, int(screen_width * 0.012))))
        
        # Try to load logo
        logo_paths = ["assets/logo.png", "logo.png", "../assets/logo.png"]
        logo_loaded = False
        
        for logo_path in logo_paths:
            if os.path.exists(logo_path):
                try:
                    logo_img = Image.open(logo_path)
                    logo_img = logo_img.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
                    logo_photo = ImageTk.PhotoImage(logo_img)
                    logo_label = tk.Label(logo_container, image=logo_photo, bg=bg_color)
                    logo_label.image = logo_photo  # Keep reference
                    logo_label.pack()
                    logo_loaded = True
                    break
                except Exception as e:
                    print(f"Failed to load logo from {logo_path}: {e}")
        
        if not logo_loaded:
            logo_font_size = max(24, int(logo_size / 3))
            tk.Label(logo_container, text="🏫", font=("Arial", logo_font_size), 
                    fg="#FFFFFF", bg=bg_color).pack()
    
    @staticmethod
    def _add_time_section(header_content, header_height, time_string, date_string, bg_color):
        """Add time display section - reusable"""
        time_container = tk.Frame(header_content, bg=bg_color)
        time_container.pack(side="right")
        
        time_font_size = max(16, int(header_height * 0.25))
        date_font_size = max(10, int(header_height * 0.15))
        
        tk.Label(time_container, textvariable=time_string, 
                font=("Arial", time_font_size, "bold"), fg="#FFFFFF", bg=bg_color).pack()
        tk.Label(time_container, textvariable=date_string, 
                font=("Arial", date_font_size), fg="#FFFFFF", bg=bg_color).pack(padx=10, pady=(0, 8))
    
    @staticmethod
    def create_verification_footer(parent, screen_info, footer_text, bg_color='#46230a'):
        """Create reusable footer for any verification GUI"""
        screen_width = screen_info['screen_width']
        screen_height = screen_info['screen_height']
        
        footer_height = max(50, int(screen_height * 0.07))
        footer = tk.Frame(parent, bg=bg_color, height=footer_height)
        footer.pack(fill="x")
        footer.pack_propagate(False)
        
        footer_font_size = max(10, int(screen_width / 85))
        tk.Label(footer, text=footer_text, font=("Arial", footer_font_size), 
                fg="#FFFFFF", bg=bg_color).pack(expand=True)
        
        return footer
    
    @staticmethod
    def create_user_info_panel(parent, screen_info, title="👤 USER AUTHENTICATED"):
        """Create reusable user info panel for any verification GUI"""
        screen_width = screen_info['screen_width']
        screen_height = screen_info['screen_height']
        
        user_info_padding_y = max(12, int(screen_height * 0.015))
        
        user_info_panel = tk.Frame(parent, bg='#e3f2fd', relief='ridge', bd=2)
        
        user_title_font = max(13, int(screen_width / 65))
        tk.Label(user_info_panel, text=title, 
                font=("Arial", user_title_font, "bold"), fg="#1565c0", bg='#e3f2fd').pack(pady=user_info_padding_y)
        
        user_details_frame = tk.Frame(user_info_panel, bg='#e3f2fd')
        details_padding_x = max(15, int(screen_width * 0.015))
        details_padding_y = max(15, int(screen_height * 0.015))
        user_details_frame.pack(padx=details_padding_x, pady=(0, details_padding_y))
        
        # Initially hidden
        user_info_panel.pack_forget()
        
        return {
            'panel': user_info_panel,
            'details_frame': user_details_frame
        }
    
    @staticmethod
    def update_user_info_display(user_details_frame, user_info, screen_info, info_fields=None):
        """Update user info display - customizable fields for different GUI types"""
        screen_width = screen_info['screen_width']
        screen_height = screen_info['screen_height']
        
        try:
            # Clear previous details
            for widget in user_details_frame.winfo_children():
                widget.destroy()
            
            # Default fields for student verification
            if info_fields is None:
                info_fields = [
                    ("Name:", 'name'),
                    ("Student ID:", 'student_id'),
                    ("Course:", 'course'),
                    ("User Type:", 'user_type')
                ]
            
            # Create info labels
            label_font_size = max(10, int(screen_width / 85))
            value_font_size = max(10, int(screen_width / 85))
            
            for label, field_key in info_fields:
                value = user_info.get(field_key, 'N/A')
                
                row_spacing = max(2, int(screen_height * 0.003))
                row = tk.Frame(user_details_frame, bg='#e3f2fd')
                row.pack(fill="x", pady=row_spacing)
                
                label_width = max(10, int(screen_width / 85))
                tk.Label(row, text=label, font=("Arial", label_font_size, "bold"), 
                        fg="#333333", bg='#e3f2fd', width=label_width, anchor="w").pack(side="left")
                tk.Label(row, text=value, font=("Arial", value_font_size), 
                        fg="#1565c0", bg='#e3f2fd').pack(side="left", padx=(8, 0))
                        
        except Exception as e:
            print(f"Error updating user info display: {e}")
