# ui/business/auth_manager.py - Authentication & Access Control Components
# KISS principle: Simple, centralized authentication logic

import tkinter as tk
from tkinter import messagebox
from datetime import datetime

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
        """Check if user role has access to a specific function
        
        Args:
            function_name: Name of the function to check
            user_role: User role (defaults to current role)
            
        Returns:
            bool: True if user has access, False otherwise
        """
        if not user_role:
            user_role = self.current_role
            
        if not user_role or user_role not in self.user_roles:
            return False
        
        role_permissions = self.user_roles[user_role]
        allowed_functions = role_permissions['allowed_functions']
        
        # Super admin has access to everything
        if allowed_functions == 'all':
            return True
        
        # Check if function is in allowed list
        return function_name in allowed_functions
    
    def get_accessible_functions(self, user_role=None):
        """Get list of functions accessible to a user role
        
        Args:
            user_role: User role (defaults to current role)
            
        Returns:
            list: List of accessible function names
        """
        if not user_role:
            user_role = self.current_role
            
        if not user_role or user_role not in self.user_roles:
            return []
        
        role_permissions = self.user_roles[user_role]
        allowed_functions = role_permissions['allowed_functions']
        
        if allowed_functions == 'all':
            # Return all possible functions for super admin
            return ['enroll', 'view_users', 'delete_fingerprint', 'sync', 
                   'get_time_records', 'clear_records', 'get_stats', 'reset',
                   'view_admins', 'enroll_guard', 'system_maintenance']
        
        return allowed_functions
    
    def authenticate_user(self, user_role, user_info=None):
        """Set authenticated user and role
        
        Args:
            user_role: Role of authenticated user
            user_info: Additional user information
            
        Returns:
            bool: True if authentication successful
        """
        if user_role not in self.user_roles:
            return False
        
        self.current_role = user_role
        self.current_user = user_info
        self.authenticated = True
        
        return True
    
    def logout(self):
        """Clear authentication"""
        self.current_user = None
        self.current_role = None
        self.authenticated = False
    
    def get_role_display_name(self, role=None):
        """Get display name for a role
        
        Args:
            role: Role name (defaults to current role)
            
        Returns:
            str: Display name for the role
        """
        if not role:
            role = self.current_role
            
        if role in self.user_roles:
            return self.user_roles[role]['name']
        
        return "Unknown Role"
    
    def is_authenticated(self):
        """Check if user is authenticated
        
        Returns:
            bool: True if authenticated
        """
        return self.authenticated
    
    def require_access(self, function_name):
        """Decorator-style access check that shows error if no access
        
        Args:
            function_name: Function name to check
            
        Returns:
            bool: True if has access, False otherwise (shows error dialog)
        """
        if not self.authenticated:
            messagebox.showerror("Authentication Required", 
                               "You must be authenticated to perform this action.")
            return False
        
        if not self.has_access(function_name):
            role_name = self.get_role_display_name()
            messagebox.showerror("Access Denied", 
                               f"Your role ({role_name}) does not have permission to {function_name}.")
            return False
        
        return True


class AuthenticationScreen:
    """Reusable authentication screen component"""
    
    def __init__(self, parent_root, colors, font_sizes, on_success_callback=None):
        self.parent_root = parent_root
        self.colors = colors
        self.font_sizes = font_sizes
        self.on_success_callback = on_success_callback
        self.auth_manager = AuthManager()
    
    def create_authentication_screen(self):
        """Create the authentication screen - RESPONSIVE
        
        Returns:
            tk.Frame: The authentication screen frame
        """
        # Clear window
        for widget in self.parent_root.winfo_children():
            widget.destroy()
        
        # Main container with gradient background
        main_container = tk.Frame(self.parent_root, bg=self.colors['primary'])
        main_container.pack(fill="both", expand=True)
        
        # Header section
        header_frame = tk.Frame(main_container, bg=self.colors['primary'])
        header_frame.pack(fill="x", pady=50)
        
        # Title
        title_label = tk.Label(header_frame, text="🔐 ADMIN AUTHENTICATION", 
                              font=("Arial", self.font_sizes['title'], "bold"),
                              fg=self.colors['gold'], bg=self.colors['primary'])
        title_label.pack()
        
        # Subtitle
        subtitle_label = tk.Label(header_frame, text="Fingerprint verification required", 
                                 font=("Arial", self.font_sizes['subtitle']),
                                 fg=self.colors['light'], bg=self.colors['primary'])
        subtitle_label.pack(pady=(5, 0))
        
        # Authentication panel
        auth_panel = tk.Frame(main_container, bg=self.colors['white'],
                             relief='raised', bd=2)
        auth_panel.pack(pady=40, padx=60, fill="both", expand=True)
        
        # Status area
        status_frame = tk.Frame(auth_panel, bg=self.colors['white'])
        status_frame.pack(fill="x", pady=30)
        
        self.status_var = tk.StringVar(value="🔐 Admin authentication required")
        status_label = tk.Label(status_frame, textvariable=self.status_var,
                               font=("Arial", self.font_sizes['subtitle']),
                               fg=self.colors['secondary'], bg=self.colors['white'])
        status_label.pack()
        
        # Instructions
        instructions_frame = tk.Frame(auth_panel, bg=self.colors['white'])
        instructions_frame.pack(fill="x", pady=20)
        
        instructions_text = ("Please place your registered admin fingerprint on the sensor.\n\n"
                           "Authorized Roles:\n"
                           "• Super Admin - Full system access\n"
                           "• Guard Admin - Limited access (Enroll & Sync only)")
        
        instructions_label = tk.Label(instructions_frame, text=instructions_text,
                                     font=("Arial", self.font_sizes['card_description']),
                                     fg=self.colors['dark'], bg=self.colors['white'],
                                     justify='center')
        instructions_label.pack()
        
        # Authentication button
        auth_button_frame = tk.Frame(auth_panel, bg=self.colors['white'])
        auth_button_frame.pack(pady=30)
        
        auth_button = tk.Button(auth_button_frame, text="🔍 START AUTHENTICATION",
                               font=("Arial", self.font_sizes['button'], "bold"),
                               bg=self.colors['info'], fg=self.colors['white'],
                               padx=40, pady=15, cursor="hand2",
                               command=self.start_authentication)
        auth_button.pack()
        
        # Cancel button
        cancel_button = tk.Button(auth_button_frame, text="❌ CANCEL",
                                 font=("Arial", self.font_sizes['button']),
                                 bg=self.colors['accent'], fg=self.colors['white'],
                                 padx=30, pady=10, cursor="hand2",
                                 command=self.cancel_authentication)
        cancel_button.pack(pady=(10, 0))
        
        return main_container
    
    def update_status(self, message, color=None):
        """Update authentication status message
        
        Args:
            message: Status message to display
            color: Optional color for the message
        """
        self.status_var.set(message)
        # You could add color changing logic here if needed
    
    def start_authentication(self):
        """Start the fingerprint authentication process"""
        self.update_status("🔍 Initializing fingerprint sensor...")
        
        # Run authentication in a separate thread to prevent GUI freezing
        import threading
        auth_thread = threading.Thread(target=self._run_authentication, daemon=True)
        auth_thread.start()
    
    def _run_authentication(self):
        """Run the actual authentication process"""
        try:
            # Import fingerprint authentication
            from etc.services.hardware.fingerprint import authenticate_admin_with_role
            
            self.parent_root.after(0, lambda: self.update_status("👆 Place admin finger on sensor..."))
            
            # Perform authentication
            user_role = authenticate_admin_with_role()
            
            if user_role:
                # Authentication successful
                self.auth_manager.authenticate_user(user_role)
                role_name = self.auth_manager.get_role_display_name(user_role)
                
                self.parent_root.after(0, lambda: self.update_status(f"✅ Authentication successful as {role_name}"))
                
                # Wait briefly then call success callback
                if self.on_success_callback:
                    self.parent_root.after(1500, lambda: self.on_success_callback(user_role))
            else:
                # Authentication failed
                self.parent_root.after(0, lambda: self.update_status("❌ Authentication failed. Please try again."))
                
        except Exception as e:
            error_msg = f"❌ Authentication error: {str(e)}"
            self.parent_root.after(0, lambda: self.update_status(error_msg))
    
    def cancel_authentication(self):
        """Cancel authentication and return to main menu"""
        try:
            self.parent_root.quit()
            self.parent_root.destroy()
        except:
            pass
    
    def get_auth_manager(self):
        """Get the authentication manager instance
        
        Returns:
            AuthManager: The authentication manager
        """
        return self.auth_manager


# Utility functions for easy integration
def create_auth_manager():
    """Factory function to create a new AuthManager
    
    Returns:
        AuthManager: New authentication manager instance
    """
    return AuthManager()

def check_access(auth_manager, function_name, show_error=True):
    """Utility function to check access with optional error display
    
    Args:
        auth_manager: AuthManager instance
        function_name: Function name to check
        show_error: Whether to show error dialog on access denied
        
    Returns:
        bool: True if has access
    """
    if show_error:
        return auth_manager.require_access(function_name)
    else:
        return auth_manager.has_access(function_name)
