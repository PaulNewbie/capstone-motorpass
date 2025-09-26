# ui/views/admin_views.py - CLEAN Views Only - NO Duplicated Functions
# FIXED: Only calls existing functions from organized files, exact UI from legacy admin_gui.py

import tkinter as tk
from tkinter import messagebox, simpledialog

# Import our organized components - USE EXISTING FUNCTIONS ONLY
from ui.components.ui_components import UIComponents
from ui.components.window_helpers import WindowIntegration
from ui.business.auth_manager import create_auth_manager, AuthenticationScreen
from ui.business.admin_operations import create_admin_handler

class AdminPanelView:
    """Clean AdminGUI - Exact UI from legacy admin_gui.py, no duplicated functions"""
    
    def __init__(self, admin_functions, skip_auth=False, user_role="super_admin"):
        self.admin_functions = admin_functions
        self.root = tk.Tk()
        
        # Use WindowIntegration for ALL setup - don't duplicate
        self.gui_setup = WindowIntegration.setup_common_gui_features(
            root=self.root,
            title="MotorPass - Admin Control Center",
            bg_color='#ECF0F1',
            enable_refresh=True
        )
        
        # Use existing AuthManager - don't duplicate
        self.auth_manager = create_auth_manager()
        
        # Use existing AdminOperationHandler - don't duplicate  
        self.operation_handler = create_admin_handler(
            admin_functions=admin_functions,
            message_handler=self.show_operation_result
        )
        
        # Get references from gui_setup - don't duplicate
        self.screen_info = self.gui_setup['screen_info']
        self.time_manager = self.gui_setup['time_manager']
        self.font_sizes = self.gui_setup['font_sizes']
        self.padding_sizes = self.gui_setup['padding_sizes']
        
        # Convenience properties from legacy
        self.screen_width = self.screen_info['screen_width']
        self.screen_height = self.screen_info['screen_height']
        self.display_size = self.screen_info['display_size']
        self.is_square_display = self.screen_info['is_square_display']
        
        # UI variables from gui_setup
        self.time_string = self.time_manager['time_string']
        self.date_string = self.time_manager['date_string']
        self.status_text = self.gui_setup['status_manager']['status_var']
        
        # Colors from legacy admin_gui.py
        self.colors = {
            'primary': '#2C3E50', 'secondary': '#34495E', 'accent': '#E74C3C',
            'success': '#27AE60', 'warning': '#F39C12', 'info': '#3498DB',
            'light': '#ECF0F1', 'dark': '#1A252F', 'gold': '#F1C40F', 'white': '#FFFFFF'
        }
        
        # Initialize - exact same logic as legacy
        if skip_auth:
            self.auth_manager.authenticate_user(user_role)
            self.show_admin_panel()
        else:
            self.show_authentication_screen()
    
    # ========================================
    # AUTHENTICATION - Use existing AuthenticationScreen
    # ========================================
    
    def show_authentication_screen(self):
        """Use existing AuthenticationScreen component"""
        self.auth_screen = AuthenticationScreen(
            parent_root=self.root,
            colors=self.colors,
            font_sizes=self.font_sizes,
            on_success_callback=self.on_authentication_success,
            admin_functions=self.admin_functions
        )
        self.auth_screen.create_authentication_screen()
    
    def on_authentication_success(self, user_role):
        """Handle successful authentication"""
        self.auth_manager.authenticate_user(user_role)
        self.show_admin_panel()
    
    # ========================================
    # MAIN INTERFACE - Use existing WindowIntegration functions
    # ========================================
    
    def show_admin_panel(self):
        """Show admin panel - EXACT layout from legacy admin_gui.py"""
        # Clear window
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Main container
        main_container = tk.Frame(self.root, bg=self.colors['light'])
        main_container.pack(fill="both", expand=True)
        
        # Use existing header function - DON'T duplicate
        WindowIntegration.create_enhanced_header(
            main_container, self.colors, self.font_sizes,
            self.time_string, self.date_string,
            title_text="🔧 MotorPass Admin Panel"
        )
        
        # Content area - exact same logic as legacy
        content_container = tk.Frame(main_container, bg=self.colors['light'])
        content_container.pack(fill="both", expand=True)
        
        if self.is_square_display:
            # Square display layout - from legacy
            self.create_stats_top_bar(content_container)
            main_content = tk.Frame(content_container, bg=self.colors['white'])
            main_content.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        else:
            # Wide display layout - from legacy
            self.create_stats_sidebar(content_container)
            main_content = tk.Frame(content_container, bg=self.colors['white'])
            main_content.pack(side="right", fill="both", expand=True, padx=(0, 15), pady=15)
        
        # Use existing menu cards function - DON'T duplicate
        self.create_menu_cards(main_content)
        
        # Use existing footer function - DON'T duplicate
        WindowIntegration.create_enhanced_footer(
            main_container, self.colors, self.font_sizes,
            user_role=self.auth_manager.get_role_display_name(),
            on_logout=self.logout_and_exit
        )
    
    def logout_and_exit(self):
        """Logout and exit"""
        self.auth_manager.logout()
        self.close()
    
    # ========================================
    # STATS DISPLAY - Only UI layout logic, no business logic
    # ========================================
    
    def create_stats_top_bar(self, parent):
        """Create stats top bar - layout only"""
        stats_height = max(60, int(self.screen_height * 0.1))
        stats_frame = tk.Frame(parent, bg=self.colors['secondary'], height=stats_height)
        stats_frame.pack(fill="x", padx=15, pady=15)
        stats_frame.pack_propagate(False)
        
        stats_content = tk.Frame(stats_frame, bg=self.colors['secondary'])
        stats_content.pack(expand=True, fill="both", pady=10)
        
        # Title
        title_font_size = max(11, int(self.display_size / 75))
        tk.Label(stats_content, text="📊 LIVE STATISTICS",
                font=("Arial", title_font_size, "bold"), fg=self.colors['white'],
                bg=self.colors['secondary']).pack()
        
        # Stats items horizontally
        self.create_stats_items_horizontal(stats_content)
    
    def create_stats_sidebar(self, parent):
        """Create stats sidebar - layout only"""
        sidebar_width = max(200, int(self.screen_width * 0.25))
        stats_frame = tk.Frame(parent, bg=self.colors['secondary'], width=sidebar_width)
        stats_frame.pack(side="left", fill="y", padx=15, pady=15)
        stats_frame.pack_propagate(False)
        
        # Title
        tk.Label(stats_frame, text="📊 SYSTEM STATUS",
                font=("Arial", self.font_sizes['card_title'], "bold"),
                fg=self.colors['light'], bg=self.colors['secondary']).pack(pady=15)
        
        # Stats items vertically
        self.create_stats_items_vertical(stats_frame)
    
    def create_stats_items_horizontal(self, parent):
        """Create horizontal stats display"""
        stats_data = self.get_stats_data()
        
        stats_container = tk.Frame(parent, bg=self.colors['secondary'])
        stats_container.pack(expand=True, pady=(5, 0))
        
        stat_font_size = max(8, int(self.display_size / 110))
        stat_value_size = max(12, int(self.display_size / 70))
        
        for icon, label, value, color in stats_data:
            stat_item = tk.Frame(stats_container, bg=self.colors['secondary'])
            stat_item.pack(side="left", padx=12)
            tk.Label(stat_item, text=f"{icon} {label}", font=("Arial", stat_font_size),
                    fg=self.colors['light'], bg=self.colors['secondary']).pack()
            tk.Label(stat_item, text=str(value), font=("Arial", stat_value_size, "bold"),
                    fg=color, bg=self.colors['secondary']).pack()
    
    def create_stats_items_vertical(self, parent):
        """Create vertical stats display"""
        stats_data = self.get_stats_data()
        
        card_spacing = max(8, int(self.screen_height / 80))
        
        for icon, label, value, color in stats_data[:4]:  # Limit to 4 for sidebar
            self.create_stat_card(parent, icon, label, value, color, card_spacing)
    
    def get_stats_data(self):
        """Get stats data - simple data gathering"""
        default_stats = [
            ("👥", "Total Users", "N/A", self.colors['info']),
            ("🔐", "Admin Status", "Active", self.colors['success']),
            ("📊", "System", "Online", self.colors['success'])
        ]
        
        # Try to get real stats if available
        if self.admin_functions and 'get_stats' in self.admin_functions:
            try:
                real_stats = self.admin_functions['get_stats']()
                if real_stats:
                    total = real_stats.get('total_students', 0) + real_stats.get('total_staff', 0)
                    default_stats[0] = ("👥", "Total Users", str(total), self.colors['info'])
            except:
                pass
        
        return default_stats
    
    def create_stat_card(self, parent, icon, label, value, color, spacing=10):
        """Create a single stat card"""
        card = tk.Frame(parent, bg=self.colors['dark'])
        card.pack(fill="x", padx=12, pady=spacing)
        
        content_padding = max(8, int(self.display_size / 100))
        content = tk.Frame(card, bg=self.colors['dark'])
        content.pack(fill="x", padx=content_padding, pady=content_padding)
        
        stat_label_size = max(9, int(self.display_size / 90))
        stat_value_size = max(16, int(self.display_size / 50))
        
        tk.Label(content, text=f"{icon} {label}",
                font=("Arial", stat_label_size), fg=self.colors['light'],
                bg=self.colors['dark']).pack(anchor="w")
        
        tk.Label(content, text=str(value),
                font=("Arial", stat_value_size, "bold"), fg=color,
                bg=self.colors['dark']).pack(anchor="w", pady=(3, 0))
    
    # ========================================
    # MENU CARDS - Use existing UIComponents
    # ========================================
    
    def create_menu_cards(self, parent):
        """Use existing UIComponents.create_menu_card_layout - DON'T duplicate"""
        # Define cards data
        all_cards_data = [
            ("👤", "Enroll New User", "Register student/staff with fingerprint",
             self.enroll_user, self.colors['success'], "enroll"),
            ("👥", "View Users", "Display all registered users",
             self.view_users, self.colors['info'], "view_users"),
            ("🗑️", "Delete User", "Remove user fingerprint",
             self.delete_user, self.colors['accent'], "delete_fingerprint"),
            ("🔄", "Sync Database", "Import from Google Sheets",
             self.sync_database, self.colors['warning'], "sync"),
            ("🕒", "Time Records", "View attendance history",
             self.view_time_records, self.colors['secondary'], "get_time_records"),
            ("🧹", "Clear Records", "Delete time records",
             self.clear_time_records, self.colors['dark'], "clear_records"),
            ("🏢", "System Maintenance", "Manage visitor offices & security codes",
             self.show_office_management, self.colors['gold'], "system_maintenance")
        ]
        
        # Filter by access
        accessible_cards = [
            card for card in all_cards_data
            if self.auth_manager.has_access(card[5])
        ]
        
        # Use existing UIComponents function - DON'T duplicate
        UIComponents.create_menu_card_layout(
            parent=parent,
            cards_data=accessible_cards,
            colors=self.colors,
            screen_width=self.screen_width,
            screen_height=self.screen_height,
            display_size=self.display_size,
            is_square_display=self.is_square_display,
            has_access_func=self.auth_manager.has_access
        )
    
    # ========================================
    # BUSINESS OPERATIONS - Call existing handlers ONLY
    # ========================================
    
    def enroll_user(self):
        """Call existing operation handler"""
        if not self.auth_manager.require_access("enroll"):
            return
        
        result = messagebox.askquestion("Enroll User",
                                       "This will start the enrollment process.\n\n" +
                                       "You will need:\n" +
                                       "• Student/Staff ID\n" +
                                       "• User's fingerprint\n\n" +
                                       "Continue?")
        if result == 'yes':
            self.operation_handler.execute_operation('enroll_user')
    
    def view_users(self):
        """Use existing UIComponents function"""
        if not self.auth_manager.require_access("view_users"):
            return
        UIComponents.create_users_display_window(
            self.root, self.colors, self.font_sizes, self.admin_functions
        )
    
    def delete_user(self):
        """Call existing operation handler"""
        if not self.auth_manager.require_access("delete_fingerprint"):
            return
        
        result = messagebox.askquestion("Delete User",
                                       "This will delete a user's fingerprint.\n\n" +
                                       "The deletion process will guide you through selecting the user.\n\n" +
                                       "Continue?")
        if result == 'yes':
            self.operation_handler.execute_operation('delete_user')
    
    def sync_database(self):
        """Call existing operation handler"""
        if not self.auth_manager.require_access("sync"):
            return
        
        result = messagebox.askquestion("Sync Database",
                                       "This will synchronize with Google Sheets database.\n\n" +
                                       "This may take a few moments.\n\n" +
                                       "Continue?")
        if result == 'yes':
            self.operation_handler.execute_operation('sync_database')
    
    def view_time_records(self):
        """Use existing UIComponents function"""
        if not self.auth_manager.require_access("get_time_records"):
            return
        UIComponents.create_time_records_window(
            self.root, self.colors, self.font_sizes, self.admin_functions
        )
    
    def clear_time_records(self):
        """Call existing operation handler"""
        if not self.auth_manager.require_access("clear_records"):
            return
        
        result = messagebox.askquestion("Clear Time Records",
                                       "This will DELETE ALL time records permanently.\n\n" +
                                       "⚠️ This action cannot be undone!\n\n" +
                                       "Continue?")
        if result == 'yes':
            self.operation_handler.execute_operation('clear_records')
    
    def show_office_management(self):
        """Create office management window using existing UIComponents"""
        if not self.auth_manager.require_access("system_maintenance"):
            return
        
        # Create window
        office_window = tk.Toplevel(self.root)
        office_window.title("🏢 Office Management")
        office_window.configure(bg=self.colors['white'])
        
        # Window sizing - from legacy
        window_sizes = {
            'width': max(800, int(self.screen_width * 0.7)),
            'height': max(600, int(self.screen_height * 0.8))
        }
        
        # Center window
        x = (self.screen_width - window_sizes['width']) // 2
        y = (self.screen_height - window_sizes['height']) // 2
        office_window.geometry(f"{window_sizes['width']}x{window_sizes['height']}+{x}+{y}")
        
        # Header
        header = tk.Frame(office_window, bg=self.colors['primary'],
                         height=max(60, int(window_sizes['height'] * 0.12)))
        header.pack(fill="x")
        header.pack_propagate(False)
        
        tk.Label(header, text="🏢 Office Management & Security Code Configuration",
                font=("Arial", self.font_sizes['subtitle']), fg=self.colors['light'],
                bg=self.colors['primary']).pack(expand=True)
        
        # Use existing UIComponents for scrollable content - DON'T duplicate
        scrollable_frame = UIComponents.create_scrollable_container(office_window, self.colors)
        
        # Office section
        office_section = tk.Frame(scrollable_frame, bg=self.colors['white'])
        office_section.pack(fill="x", padx=15, pady=15)
        
        # Use existing UIComponents for office management - DON'T duplicate
        UIComponents.create_office_management_section(
            parent=office_section,
            colors=self.colors,
            font_sizes=self.font_sizes
        )
        
        # Close button
        close_frame = tk.Frame(scrollable_frame, bg=self.colors['white'])
        close_frame.pack(fill="x", padx=15, pady=15)
        
        tk.Button(close_frame, text="❌ Close", command=office_window.destroy,
                 bg=self.colors['dark'], fg="white", font=("Arial", self.font_sizes['button'], "bold"),
                 cursor="hand2", padx=20, pady=8).pack()
    
    def show_operation_result(self, title, message, is_error=False):
        """Show operation result"""
        if is_error:
            messagebox.showerror(title, message)
        else:
            messagebox.showinfo(title, message)
    
    # ========================================
    # CONTROL METHODS
    # ========================================
    
    def run(self):
        """Run the GUI"""
        try:
            self.root.bind('<Escape>', lambda e: self.close())
            self.root.mainloop()
        except Exception as e:
            print(f"Error running GUI: {e}")
            self.close()
    
    def close(self):
        """Close the GUI"""
        try:
            self.auth_manager.logout()
            self.root.quit()
            self.root.destroy()
        except:
            pass


# Backward compatibility
AdminPanelGUI = AdminPanelView

class AdminPanelGUI(AdminPanelView):
    """Backward compatibility class"""
    pass
