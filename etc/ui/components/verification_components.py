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
        
        # Auto-update when status changes - FIXED: Use thread-safe approach
        def update_callback(*args):
            try:
                # Get the current status value
                current_status = status_var.get()
                # Update the display in the main thread
                VerificationUIComponents.update_status_display(badge, icon_label, current_status)
            except Exception as e:
                print(f"Error updating status display: {e}")
        
        status_var.trace_add("write", update_callback)
        
        return {
            'item_frame': item_frame,
            'label': label,
            'badge': badge,
            'icon': icon_label
        }
    
    @staticmethod
    def update_status_display(badge, icon, status):
        """Update status display with enhanced styling - reusable for any verification GUI"""
        status_configs = {
            "VERIFIED": ("#27ae60", "✅", "#27ae60"),
            "FAILED": ("#e74c3c", "❌", "#e74c3c"),
            "CHECKING": ("#f39c12", "🔄", "#f39c12"),
            "PROCESSING": ("#3498db", "⏳", "#3498db"),
            "PENDING": ("#95a5a6", "⏸", "#95a5a6"),
            "TIMEOUT": ("#e67e22", "⏰", "#e67e22"),
            "ERROR": ("#c0392b", "⚠️", "#c0392b")
        }
        
        try:
            if status in status_configs:
                bg_color, icon_text, icon_color = status_configs[status]
                # Enhanced badge styling with subtle shadow effect
                badge.config(text=status, bg=bg_color, relief='solid', bd=1)
                icon.config(text=icon_text, fg=icon_color)
                
                # Add subtle animation effect for active statuses
                if status in ["CHECKING", "PROCESSING"]:
                    # Subtle pulsing effect for active statuses
                    badge.config(relief='raised', bd=2)
                else:
                    badge.config(relief='solid', bd=1)
            else:
                # Fallback for unknown status
                badge.config(text=status, bg="#6c757d", relief='solid', bd=1)
                icon.config(text="❓", fg="#6c757d")
        except Exception as e:
            print(f"Error updating status display widgets: {e}")
    
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
        header_content.pack(fill="both", expand=True, padx=header_padding, pady=max(8, int(header_height * 0.1)))
        
        # Logo section with fallback
        logo_size = max(50, int(header_height * 0.7))
        logo_container = tk.Frame(header_content, bg=bg_color, width=logo_size, height=logo_size)
        logo_container.pack(side="left", padx=(0, header_padding))
        logo_container.pack_propagate(False)
        
        # Try to load logo image, fallback to text
        logo_loaded = False
        for logo_path in ["images/motorpass_logo.png", "assets/logo.png", "logo.png"]:
            if os.path.exists(logo_path):
                try:
                    logo_img = Image.open(logo_path).resize((logo_size, logo_size), Image.Resampling.LANCZOS)
                    logo_photo = ImageTk.PhotoImage(logo_img)
                    logo_label = tk.Label(logo_container, image=logo_photo, bg=bg_color)
                    logo_label.image = logo_photo  # Keep reference
                    logo_label.pack()
                    logo_loaded = True
                    break
                except:
                    pass
        
        if not logo_loaded:
            # Fallback text logo
            logo_frame = tk.Frame(logo_container, bg='#DAA520', width=logo_size, height=logo_size)
            logo_frame.pack()
            logo_frame.pack_propagate(False)
            fallback_font_size = max(20, int(logo_size * 0.35))
            tk.Label(logo_frame, text="MP", font=("Arial", fallback_font_size, "bold"), 
                    fg=bg_color, bg="#DAA520").place(relx=0.5, rely=0.5, anchor="center")
        
        # Title section
        title_frame = tk.Frame(header_content, bg=bg_color)
        title_frame.pack(side="left", fill="both", expand=True)
        
        main_title_font = max(20, int(screen_width / 40))
        subtitle_font = max(9, int(screen_width / 100))
        
        tk.Label(title_frame, text="MotorPass", font=("Arial", main_title_font, "bold"), 
                fg="#DAA520", bg=bg_color).pack(anchor="w")
        tk.Label(title_frame, text=subtitle,
                font=("Arial", subtitle_font), fg="#FFFFFF", bg=bg_color).pack(anchor="w")
        
        # Clock
        clock_width = max(140, int(screen_width * 0.14))
        clock_height = max(65, int(header_height * 0.8))
        
        clock_frame = tk.Frame(header_content, bg=bg_color, bd=2, relief='solid',
                              width=clock_width, height=clock_height)
        clock_frame.pack(side="right")
        clock_frame.pack_propagate(False)
        
        time_font_size = max(14, int(screen_width / 55))
        date_font_size = max(9, int(screen_width / 100))
        
        tk.Label(clock_frame, textvariable=time_string, font=("Arial", time_font_size, "bold"), 
                fg="#DAA520", bg=bg_color).pack(padx=10, pady=(8, 3))
        tk.Label(clock_frame, textvariable=date_string, font=("Arial", date_font_size), 
                fg="#FFFFFF", bg=bg_color).pack(padx=10, pady=(3, 8))
        
        return header
    
    @staticmethod
    def create_user_info_panel(parent, screen_info, title="USER INFO"):
        """Create reusable user info panel for any verification GUI"""
        screen_width = screen_info['screen_width']
        screen_height = screen_info['screen_height']
        
        # User info container
        info_panel = tk.Frame(parent, bg='#3498db', relief='raised', bd=2)
        
        # Title
        title_font_size = max(12, int(screen_width / 75))
        title_padding = max(10, int(screen_height * 0.015))
        
        tk.Label(info_panel, text=title, font=("Arial", title_font_size, "bold"), 
                fg="#FFFFFF", bg='#3498db').pack(pady=title_padding)
        
        # Details container
        details_padding_x = max(15, int(screen_width * 0.015))
        details_padding_y = max(10, int(screen_height * 0.012))
        
        details_frame = tk.Frame(info_panel, bg='#3498db')
        details_frame.pack(fill="x", padx=details_padding_x, pady=(0, details_padding_y))
        
        return {
            'panel': info_panel,
            'details_frame': details_frame
        }
    
    @staticmethod
    def update_user_info_display(user_details_frame, user_info, screen_info, info_fields):
        """Update user info display - reusable for any verification GUI"""
        screen_width = screen_info['screen_width']
        
        # Clear existing details
        for widget in user_details_frame.winfo_children():
            widget.destroy()
        
        # Add user info fields
        detail_font_size = max(9, int(screen_width / 100))
        detail_spacing = max(4, int(screen_info['screen_height'] * 0.006))
        
        for field_label, field_key in info_fields:
            value = user_info.get(field_key, 'N/A')
            detail_text = f"{field_label} {value}"
            tk.Label(user_details_frame, text=detail_text, font=("Arial", detail_font_size), 
                    fg="#FFFFFF", bg='#3498db').pack(anchor="w", pady=detail_spacing)
    
    @staticmethod
    def create_verification_footer(parent, screen_info, footer_text="Verification in progress..."):
        """Create reusable footer for any verification GUI"""
        screen_width = screen_info['screen_width']
        screen_height = screen_info['screen_height']
        
        footer_height = max(40, int(screen_height * 0.05))
        footer = tk.Frame(parent, bg='#34495e', height=footer_height)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)
        
        footer_font_size = max(10, int(screen_width / 80))
        footer_padding = max(10, int(screen_width * 0.01))
        
        tk.Label(footer, text=footer_text, font=("Arial", footer_font_size), 
                fg="#ecf0f1", bg='#34495e').pack(pady=max(8, int(footer_height * 0.2)), padx=footer_padding)
        
        return footer
    
    @staticmethod
    def create_student_info_panel(parent, screen_info, current_step_var):
        """Create enhanced but clean student information panel"""
        screen_width = screen_info['screen_width']
        screen_height = screen_info['screen_height']
        
        # Student information container with consistent styling
        info_container = tk.Frame(parent, bg='white', relief='raised', bd=3)
        info_container.pack(fill="both", expand=True)
        
        # Header with consistent styling (matches other panels)
        title_font_size = max(16, int(screen_width / 50))
        title_padding_y = max(15, int(screen_height * 0.02))
        
        tk.Label(info_container, text="STUDENT/STAFF INFORMATION", 
                font=("Arial", title_font_size, "bold"), fg="#333333", bg='white').pack(pady=title_padding_y)
        
        # Main content area with better styling
        content_area = tk.Frame(info_container, bg='white')
        content_area.pack(fill="both", expand=True, padx=25, pady=(0, 25))
        
        # Welcome card
        welcome_card = tk.Frame(content_area, bg='#f8f9fa', relief='solid', bd=1)
        welcome_card.pack(fill="x", pady=(0, 20))
        
        # Welcome message with icon
        welcome_font_size = max(16, int(screen_width / 55))
        welcome_label = tk.Label(welcome_card, 
                                text="🎓 Welcome to MotorPass\nStudent & Staff Verification System", 
                                font=("Arial", welcome_font_size, "bold"), fg="#2c3e50", bg='#f8f9fa',
                                justify="center")
        welcome_label.pack(pady=25)
        
        # Student details frame (for when user info is available)
        details_frame = tk.Frame(content_area, bg='white')
        
        return {
            'container': info_container,
            'content_area': content_area,
            'welcome_label': welcome_label,
            'details_frame': details_frame,
            'welcome_card': welcome_card
        }
    
    @staticmethod
    def update_student_info_display(details_frame, welcome_label, step_label, user_info, screen_info, welcome_card=None, status_card=None):
        """Update student information display - clean and focused"""
        try:
            # Hide welcome card
            if welcome_card:
                welcome_card.pack_forget()
            else:
                welcome_label.pack_forget()
            
            # Clear previous details
            for widget in details_frame.winfo_children():
                widget.destroy()
            
            # Show the details frame with enhanced styling
            details_frame.configure(bg='white', relief='solid', bd=1)
            details_frame.pack(fill="x", pady=(0, 20))
            
            # User info header
            header_frame = tk.Frame(details_frame, bg='#27ae60', height=50)
            header_frame.pack(fill="x")
            header_frame.pack_propagate(False)
            
            header_font_size = max(14, int(screen_info['screen_width'] / 60))
            tk.Label(header_frame, text="✅ Identity Verified", 
                    font=("Arial", header_font_size, "bold"), fg="white", bg='#27ae60').pack(expand=True)
            
            # User details content
            content_frame = tk.Frame(details_frame, bg='white')
            content_frame.pack(fill="x", padx=20, pady=20)
            
            # User name - prominently displayed with icon
            name_font_size = max(18, int(screen_info['screen_width'] / 50))
            name = user_info.get('name', 'N/A')
            name_label = tk.Label(content_frame, text=f"👋 Hello, {name}!", 
                                 font=("Arial", name_font_size, "bold"), fg="#2c3e50", bg='white')
            name_label.pack(pady=(0, 15))
            
            # Info container with subtle background
            info_container = tk.Frame(content_frame, bg='#f1f2f6', relief='flat', bd=1)
            info_container.pack(fill="x", pady=(0, 15))
            
            # User details with better formatting
            info_font_size = max(11, int(screen_info['screen_width'] / 75))
            
            # User type and ID in a nice layout
            user_type = user_info.get('user_type', 'Student')
            user_id = user_info.get('student_id', user_info.get('unified_id', 'N/A'))
            
            id_frame = tk.Frame(info_container, bg='#f1f2f6')
            id_frame.pack(fill="x", padx=15, pady=10)
            
            tk.Label(id_frame, text="🆔", font=("Arial", 14), fg="#3498db", bg='#f1f2f6').pack(side="left")
            tk.Label(id_frame, text=f"  {user_type} ID: {user_id}", 
                    font=("Arial", info_font_size, "bold"), fg="#2c3e50", bg='#f1f2f6').pack(side="left")
            
            # Course/Department (if available)
            if user_info.get('course') and user_info.get('course') != 'N/A':
                course_frame = tk.Frame(info_container, bg='#f1f2f6')
                course_frame.pack(fill="x", padx=15, pady=(0, 10))
                
                tk.Label(course_frame, text="📚", font=("Arial", 14), fg="#e74c3c", bg='#f1f2f6').pack(side="left")
                tk.Label(course_frame, text=f"  {user_info.get('course')}", 
                        font=("Arial", info_font_size), fg="#2c3e50", bg='#f1f2f6').pack(side="left")
            
            # Add a subtle success message
            success_font_size = max(10, int(screen_info['screen_width'] / 80))
            tk.Label(content_frame, text="🔐 Proceeding with verification process...", 
                    font=("Arial", success_font_size, "italic"), fg="#7f8c8d", bg='white').pack(pady=(10, 0))
                
        except Exception as e:
            print(f"Error showing student info: {e}")
