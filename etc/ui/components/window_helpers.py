# ui/components/window_helpers.py - Window Management Components
# FIXED: Complete implementation matching legacy admin_gui.py

import tkinter as tk
from datetime import datetime

class WindowManager:
    """Reusable window management components for consistent behavior across all GUIs"""
    
    @staticmethod
    def setup_fullscreen_window(root, title, bg_color='#FFFFFF'):
        """Setup a responsive fullscreen window with consistent behavior - from legacy admin_gui.py"""
        root.title(title)
        root.configure(bg=bg_color)
        
        # Get screen dimensions
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        
        # Calculate display characteristics
        aspect_ratio = screen_width / screen_height
        is_square_display = abs(aspect_ratio - 1.0) < 0.3  # Within 30% of square (1024x768 = 1.33)
        is_wide_display = aspect_ratio > 1.5  # Wider than 3:2
        
        # Set base size for responsive calculations
        if is_square_display:
            display_size = min(screen_width, screen_height)
        else:
            display_size = min(screen_width, screen_height)
        
        # Set fullscreen geometry
        root.geometry(f"{screen_width}x{screen_height}")
        root.resizable(False, False)
        
        # Make window fullscreen and hide taskbar - from legacy admin_gui.py
        try:
            # Try Windows method first
            root.state('zoomed')
            # Hide taskbar by making window truly fullscreen
            root.attributes('-fullscreen', True)
        except:
            # Fallback for other platforms
            try:
                root.attributes('-zoomed', True)
                root.attributes('-fullscreen', True)
            except:
                # Final fallback - just maximize
                root.state('normal')
                root.geometry(f"{screen_width}x{screen_height}+0+0")
        
        # Return screen information for responsive calculations
        return {
            'screen_width': screen_width,
            'screen_height': screen_height,
            'aspect_ratio': aspect_ratio,
            'is_square_display': is_square_display,
            'is_wide_display': is_wide_display,
            'display_size': display_size
        }


class ResponsiveCalculator:
    """Calculate responsive sizes based on screen dimensions - from legacy admin_gui.py"""
    
    @staticmethod
    def calculate_font_sizes(display_size):
        """Calculate responsive font sizes"""
        return {
            'title': max(24, int(display_size / 30)),
            'subtitle': max(16, int(display_size / 50)),
            'card_title': max(14, int(display_size / 60)),
            'card_description': max(10, int(display_size / 80)),
            'button': max(12, int(display_size / 70)),
            'time': max(14, int(display_size / 60)),
            'date': max(10, int(display_size / 80)),
            'stat_label': max(9, int(display_size / 90)),
            'stat_value': max(16, int(display_size / 50))
        }
    
    @staticmethod
    def calculate_padding_sizes(screen_width, screen_height):
        """Calculate responsive padding sizes"""
        return {
            'content_x': max(15, int(screen_width * 0.02)),
            'content_y': max(15, int(screen_height * 0.02)),
            'card_spacing': max(6, int(screen_width * 0.008)),
            'section_spacing': max(20, int(screen_width * 0.03)),
            'header_padding': max(15, int(screen_height * 0.02)),
            'title_padding': max(15, int(screen_height * 0.02))
        }


class WindowIntegration:
    """Integration class for common GUI features - from legacy admin_gui.py"""
    
    @staticmethod
    def setup_common_gui_features(root, title, bg_color='#ECF0F1', enable_refresh=True):
        """Setup common GUI features like time display, screen info, etc."""
        
        # Setup window with fullscreen
        screen_info = WindowManager.setup_fullscreen_window(root, title, bg_color)
        
        # Calculate responsive sizes
        font_sizes = ResponsiveCalculator.calculate_font_sizes(screen_info['display_size'])
        padding_sizes = ResponsiveCalculator.calculate_padding_sizes(
            screen_info['screen_width'], screen_info['screen_height'])
        
        # Time management variables
        time_string = tk.StringVar()
        date_string = tk.StringVar()
        status_var = tk.StringVar()
        
        def update_time():
            """Update time display"""
            now = datetime.now()
            time_string.set(now.strftime("%I:%M:%S %p"))
            date_string.set(now.strftime("%A, %B %d, %Y"))
            if enable_refresh:
                root.after(1000, update_time)
        
        # Start time updates
        update_time()
        
        return {
            'screen_info': screen_info,
            'font_sizes': font_sizes,
            'padding_sizes': padding_sizes,
            'time_manager': {
                'time_string': time_string,
                'date_string': date_string,
                'update_time': update_time
            },
            'status_manager': {
                'status_var': status_var
            }
        }
    
    @staticmethod
    def create_enhanced_header(parent, colors, font_sizes, time_string, date_string, 
                              title_text="MotorPass Admin Panel"):
        """Create enhanced header with time display - EXACT from legacy admin_gui.py"""
        # Responsive header height - EXACT calculation from legacy
        header_height = max(60, int(parent.winfo_screenheight() * 0.08))
        header = tk.Frame(parent, bg=colors['primary'], height=header_height)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        # Add subtle shadow - EXACT from legacy
        shadow = tk.Frame(parent, bg='#E0E0E0', height=2)
        shadow.pack(fill="x")
        
        # Header content with responsive padding - EXACT from legacy
        screen_width = parent.winfo_screenwidth()
        header_padding = max(15, int(screen_width * 0.02))
        header_content = tk.Frame(header, bg=colors['primary'])
        header_content.pack(fill="both", expand=True, padx=header_padding)
        
        # Logo and title section - EXACT from legacy
        left_section = tk.Frame(header_content, bg=colors['primary'])
        left_section.pack(side="left", fill="y")
        
        # Modern logo with responsive sizing - EXACT from legacy
        logo_size = max(40, int(header_height * 0.6))
        logo_bg = tk.Frame(left_section, bg=colors['gold'], width=logo_size, height=logo_size)
        logo_bg.pack(side="left", pady=(header_height - logo_size) // 2)
        logo_bg.pack_propagate(False)
        
        # Get display size for responsive calculation
        display_size = min(screen_width, parent.winfo_screenheight())
        logo_icon_size = max(16, int(logo_size * 0.4))
        tk.Label(logo_bg, text="⚡", font=("Arial", logo_icon_size), 
                bg=colors['gold'], fg=colors['primary']).place(relx=0.5, rely=0.5, anchor="center")
        
        # Title with responsive fonts - EXACT from legacy
        title_section = tk.Frame(left_section, bg=colors['primary'])
        title_section.pack(side="left", padx=(15, 0), fill="y")
        
        title_font_size = max(16, int(display_size / 50))
        subtitle_font_size = max(8, int(display_size / 100))
        
        title_y_padding = (header_height - 40) // 2
        tk.Label(title_section, text="ADMIN CONTROL CENTER", 
                font=("Arial", title_font_size, "bold"), fg=colors['white'], bg=colors['primary']).pack(anchor="w", pady=(title_y_padding, 0))
        tk.Label(title_section, text="MotorPass Management System",
                font=("Arial", subtitle_font_size), fg=colors['light'], bg=colors['primary']).pack(anchor="w")
        
        # Right section with clock - EXACT from legacy
        right_section = tk.Frame(header_content, bg=colors['primary'])
        right_section.pack(side="right", fill="y")
        
        # Modern clock display with responsive sizing - EXACT from legacy
        clock_width = max(140, int(screen_width * 0.12))
        clock_height = max(50, int(header_height * 0.7))
        clock_container = tk.Frame(right_section, bg=colors['secondary'], relief='flat',
                                  width=clock_width, height=clock_height)
        clock_container.pack(pady=(header_height - clock_height) // 2, padx=8)
        clock_container.pack_propagate(False)
        
        time_frame = tk.Frame(clock_container, bg=colors['secondary'])
        time_frame.pack(expand=True)
        
        time_font_size = max(12, int(display_size / 65))
        date_font_size = max(7, int(display_size / 120))
        
        tk.Label(time_frame, textvariable=time_string, font=("Arial", time_font_size, "bold"), 
                fg=colors['gold'], bg=colors['secondary']).pack(pady=(8, 0))
        tk.Label(time_frame, textvariable=date_string, font=("Arial", date_font_size), 
                fg=colors['light'], bg=colors['secondary']).pack()
        
        return header
    
    @staticmethod
    def create_enhanced_footer(parent, colors, font_sizes, user_role=None, on_logout=None):
        """Create enhanced footer - EXACT from legacy admin_gui.py"""
        # Footer with responsive height - EXACT calculation from legacy
        screen_height = parent.winfo_screenheight()
        display_size = min(parent.winfo_screenwidth(), screen_height)
        footer_height = max(50, int(screen_height * 0.08))
        footer = tk.Frame(parent, bg=colors['dark'], height=footer_height)
        footer.pack(fill="x")
        footer.pack_propagate(False)
        
        footer_content = tk.Frame(footer, bg=colors['dark'])
        footer_content.pack(expand=True)
        
        # Buttons with modern style and responsive sizing - EXACT from legacy
        buttons_frame = tk.Frame(footer_content, bg=colors['dark'])
        buttons_frame.pack(pady=(footer_height - 35) // 2)
        
        # Responsive button sizing - EXACT from legacy
        button_font_size = max(10, int(display_size / 80))
        button_padding_x = max(20, int(display_size / 40))
        button_padding_y = max(8, int(display_size / 100))
        
        # Dashboard button (only for super admin) - EXACT from legacy
        if user_role == "Super Admin":
            dash_btn = tk.Button(buttons_frame, text="📊 WEB DASHBOARD", 
                                font=("Arial", button_font_size, "bold"), 
                                bg=colors['gold'], fg=colors['dark'],
                                activebackground=colors['warning'],
                                padx=button_padding_x, pady=button_padding_y, cursor="hand2", relief='flat', bd=0,
                                command=lambda: open_dashboard())
            dash_btn.pack(side="left", padx=8)
            
            # Add hover effects
            dash_btn.bind("<Enter>", lambda e: dash_btn.config(bg=colors['warning']))
            dash_btn.bind("<Leave>", lambda e: dash_btn.config(bg=colors['gold']))
        
        # Exit button (always show) - EXACT from legacy
        exit_btn = tk.Button(buttons_frame, text="🚪 EXIT ADMIN PANEL", 
                            font=("Arial", button_font_size, "bold"), 
                            bg=colors['accent'], fg=colors['white'],
                            activebackground='#C0392B',
                            padx=button_padding_x, pady=button_padding_y, cursor="hand2", relief='flat', bd=0,
                            command=on_logout if on_logout else lambda: None)
        exit_btn.pack(side="left", padx=8)
        
        # Add hover effects for exit button
        exit_btn.bind("<Enter>", lambda e: exit_btn.config(bg='#C0392B'))
        exit_btn.bind("<Leave>", lambda e: exit_btn.config(bg=colors['accent']))
        
        return footer

def open_dashboard():
    """Open web dashboard - helper function for footer"""
    import webbrowser
    try:
        webbrowser.open("http://localhost:5000")
        import tkinter.messagebox
        tkinter.messagebox.showinfo("Dashboard Opened", 
                          "Web dashboard opened in your browser!\n\n" +
                          "Default login: admin / motorpass123",
                          icon='info')
    except:
        import tkinter.messagebox
        tkinter.messagebox.showerror("Error", "Failed to open web dashboard")
