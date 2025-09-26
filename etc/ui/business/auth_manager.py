# ui/business/auth_manager.py - Authentication & Access Control Components
# FIXED: Complete implementation matching legacy admin_gui.py

import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import threading
import time

class AuthManager:
    """Centralized authentication and access control management"""
    
    def __init__(self):
        self.user_roles = {
            'super_admin': {
                'name': 'Super Admin',
                'description': 'Full system access',
                'allowed_functions': 'all'
            },
            'guard': {
                'name': 'Security Guard',
                'description': 'Limited access to enroll and sync',
                'allowed_functions': ['enroll', 'sync']
            },
            'admin': {
                'name': 'Administrator',
                'description': 'System administration',
                'allowed_functions': ['enroll', 'view_users', 'delete_fingerprint', 'sync', 'get_time_records']
            }
        }
        
        self.current_user = None
        self.current_role = None
        self.authenticated = False
    
    def has_access(self, function_name, user_role=None):
        """Check if user role has access to a specific function"""
        if not user_role:
            user_role = self.current_role
            
        if not user_role or user_role not in self.user_roles:
            return False
        
        role_permissions = self.user_roles[user_role]
        allowed_functions = role_permissions['allowed_functions']
        
        # Super admin has access to everything
        if allowed_functions == 'all':
            return True
        
        # Check specific function permissions
        return function_name in allowed_functions
    
    def authenticate_user(self, user_role):
        """Authenticate user with given role"""
        if user_role in self.user_roles:
            self.current_role = user_role
            self.authenticated = True
            return True
        return False
    
    def logout(self):
        """Logout current user"""
        self.current_user = None
        self.current_role = None
        self.authenticated = False
    
    def get_role_display_name(self):
        """Get display name for current role"""
        if self.current_role and self.current_role in self.user_roles:
            return self.user_roles[self.current_role]['name']
        return "Unknown"
    
    def require_access(self, function_name):
        """Require access to function, show error if denied"""
        if not self.authenticated:
            messagebox.showerror("Authentication Required", "Please authenticate first.")
            return False
        
        if not self.has_access(function_name):
            role_name = self.get_role_display_name()
            messagebox.showerror("Access Denied", 
                               f"Your role ({role_name}) does not have permission to {function_name}.")
            return False
        
        return True


class AuthenticationScreen:
    """Reusable authentication screen component - FIXED from legacy admin_gui.py"""
    
    def __init__(self, parent_root, colors, font_sizes, on_success_callback=None, admin_functions=None):
        self.parent_root = parent_root
        self.colors = colors
        self.font_sizes = font_sizes
        self.on_success_callback = on_success_callback
        self.admin_functions = admin_functions
        self.auth_manager = AuthManager()
        
        # Create variables
        self.status_text = tk.StringVar(value="🔐 Admin authentication required")
        self.authenticated = False
    
    def create_authentication_screen(self):
        """Create the authentication screen - EXACT from legacy admin_gui.py"""
        # Clear window
        for widget in self.parent_root.winfo_children():
            widget.destroy()
        
        # Main container with gradient background - EXACT from legacy
        main_container = tk.Frame(self.parent_root, bg=self.colors['primary'])
        main_container.pack(fill="both", expand=True)
        
        # Create gradient effect - EXACT from legacy
        gradient_frame = tk.Canvas(main_container, highlightthickness=0)
        gradient_frame.pack(fill="both", expand=True)
        
        # Responsive card sizing - EXACT from legacy
        screen_width = self.parent_root.winfo_screenwidth()
        screen_height = self.parent_root.winfo_screenheight()
        display_size = min(screen_width, screen_height)
        aspect_ratio = screen_width / screen_height
        is_square_display = abs(aspect_ratio - 1.0) < 0.3
        
        if is_square_display:
            card_width = int(display_size * 0.5)
            card_height = int(display_size * 0.55)
        else:
            card_width = int(display_size * 0.45)
            card_height = int(display_size * 0.5)
            
        # Authentication card - EXACT from legacy
        auth_card = tk.Frame(gradient_frame, bg=self.colors['white'], relief='flat')
        auth_card.place(relx=0.5, rely=0.5, anchor='center', width=card_width, height=card_height)
        
        # Card shadow effect - EXACT from legacy
        shadow = tk.Frame(gradient_frame, bg='#D0D0D0')
        shadow.place(relx=0.5, rely=0.5, anchor='center', width=card_width+10, height=card_height+10)
        auth_card.lift()
        
        # Responsive logo section - EXACT from legacy
        logo_height = max(100, int(card_height * 0.25))
        logo_frame = tk.Frame(auth_card, bg=self.colors['primary'], height=logo_height)
        logo_frame.pack(fill="x")
        logo_frame.pack_propagate(False)
        
        # Logo with responsive size - EXACT from legacy
        logo_size = max(60, int(logo_height * 0.6))
        logo_container = tk.Frame(logo_frame, bg=self.colors['gold'], width=logo_size, height=logo_size)
        logo_container.place(relx=0.5, rely=0.5, anchor='center')
        
        logo_icon_size = max(24, int(logo_size * 0.4))
        tk.Label(logo_container, text="🛡️", font=("Arial", logo_icon_size), 
                bg=self.colors['gold'], fg=self.colors['primary']).place(relx=0.5, rely=0.5, anchor='center')
        
        # Responsive fonts - EXACT from legacy
        title_font_size = max(18, int(display_size / 45))
        subtitle_font_size = max(11, int(display_size / 70))
        status_font_size = max(10, int(display_size / 80))
        button_font_size = max(12, int(display_size / 65))
        
        # Title - EXACT from legacy
        title_padding = max(20, int(card_height * 0.05))
        tk.Label(auth_card, text="ADMIN ACCESS CONTROL", 
                font=("Arial", title_font_size, "bold"), fg=self.colors['primary'], bg=self.colors['white']).pack(pady=(title_padding, 8))
        
        # Subtitle - EXACT from legacy
        tk.Label(auth_card, text="Fingerprint Authentication Required", 
                font=("Arial", subtitle_font_size), fg=self.colors['secondary'], bg=self.colors['white']).pack(pady=(0, title_padding))
        
        # Status with animated dots - EXACT from legacy
        status_frame = tk.Frame(auth_card, bg=self.colors['white'])
        status_frame.pack(pady=15)
        
        self.status_label = tk.Label(status_frame, textvariable=self.status_text, 
                                    font=("Arial", status_font_size), fg=self.colors['info'], bg=self.colors['white'])
        self.status_label.pack()
        
        # Authentication button with hover effect - EXACT from legacy
        auth_btn_frame = tk.Frame(auth_card, bg=self.colors['white'])
        auth_btn_frame.pack(pady=title_padding)
        
        button_padding_x = max(25, int(card_width * 0.08))
        button_padding_y = max(12, int(card_height * 0.03))
        
        self.auth_button = tk.Button(auth_btn_frame, text="🔓 START AUTHENTICATION", 
                                    font=("Arial", button_font_size, "bold"), 
                                    bg=self.colors['success'], fg=self.colors['white'],
                                    activebackground=self.colors['info'],
                                    activeforeground=self.colors['white'],
                                    padx=button_padding_x, pady=button_padding_y, cursor="hand2",
                                    relief='flat', bd=0,
                                    command=self.start_authentication)
        self.auth_button.pack()
        
        # Add hover effects - EXACT from legacy
        self.auth_button.bind("<Enter>", lambda e: self.auth_button.config(bg=self.colors['info']))
        self.auth_button.bind("<Leave>", lambda e: self.auth_button.config(bg=self.colors['success']))
        
        # Exit button - EXACT from legacy
        exit_font_size = max(9, int(display_size / 90))
        exit_padding = max(15, int(card_width * 0.06))
        
        exit_btn = tk.Button(auth_card, text="EXIT", 
                            font=("Arial", exit_font_size), bg=self.colors['secondary'], fg=self.colors['white'],
                            activebackground=self.colors['accent'],
                            padx=exit_padding, pady=6, cursor="hand2", relief='flat', bd=0,
                            command=lambda: self.parent_root.destroy())
        exit_btn.pack(pady=(0, 15))
        
        return main_container
        
    def start_authentication(self):
        """Start fingerprint authentication process - from legacy admin_gui.py"""
        self.auth_button.config(state='disabled', text="🔍 SCANNING...")
        self.status_text.set("👆 Place finger on sensor...")
        
        # Start authentication in thread
        auth_thread = threading.Thread(target=self.perform_authentication, daemon=True)
        auth_thread.start()
    
    def perform_authentication(self):
        """Perform actual fingerprint authentication - from legacy admin_gui.py"""
        try:
            if self.admin_functions and 'authenticate_admin' in self.admin_functions:
                # Use admin function for authentication
                result = self.admin_functions['authenticate_admin']()
                
                if result and result.get('success'):
                    user_role = result.get('role', 'super_admin')
                    self.parent_root.after(0, lambda: self.authentication_success(user_role))
                else:
                    self.parent_root.after(0, lambda: self.authentication_failed())
            else:
                # Fallback for testing - skip auth after 2 seconds
                time.sleep(2)
                self.parent_root.after(0, lambda: self.authentication_success('super_admin'))
                
        except Exception as e:
            self.parent_root.after(0, lambda: self.status_text.set(f"❌ Error: {str(e)}"))
            self.parent_root.after(0, lambda: self.auth_button.config(state='normal', text="🔓 START AUTHENTICATION"))
    
    def authentication_success(self, user_role):
        """Handle successful authentication"""
        self.authenticated = True
        self.auth_manager.authenticate_user(user_role)
        
        if self.on_success_callback:
            self.on_success_callback(user_role)
    
    def authentication_failed(self):
        """Handle failed authentication"""
        self.status_text.set("❌ Access denied. Try again.")
        self.auth_button.config(state='normal', text="🔓 START AUTHENTICATION")
        self.parent_root.after(3000, lambda: self.status_text.set("🔐 Admin authentication required"))


# Factory functions for easy creation
def create_auth_manager():
    """Create and return a new AuthManager instance"""
    return AuthManager()

def create_authentication_screen(parent_root, colors, font_sizes, on_success_callback=None, admin_functions=None):
    """Create and return a new AuthenticationScreen instance"""
    return AuthenticationScreen(parent_root, colors, font_sizes, on_success_callback, admin_functions)
