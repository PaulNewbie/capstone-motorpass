# ui/views/admin_view.py - Fully Refactored AdminGUI
# Clean separation: UI only, business logic extracted

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

# Import our reusable components
from ui.components.ui_components import UIComponents
from ui.components.window_helpers import WindowManager, ResponsiveCalculator, WindowIntegration
from ui.business.auth_manager import AuthManager, AuthenticationScreen, create_auth_manager
from ui.business.admin_operations import AdminOperationHandler, create_admin_handler

class AdminPanelView:
    """Clean AdminGUI - Only UI logic, no business logic"""
    
    def __init__(self, admin_functions, skip_auth=False, user_role="super_admin"):
        self.admin_functions = admin_functions
        self.root = tk.Tk()
        
        # ========================================
        # COMPONENT SETUP - All in one place
        # ========================================
        
        # Window management
        self.gui_setup = WindowIntegration.setup_common_gui_features(
            root=self.root,
            title="MotorPass - Admin Control Center",
            bg_color='#ECF0F1',
            enable_refresh=True
        )
        
        # Authentication management
        self.auth_manager = create_auth_manager()
        
        # Business logic handler
        self.operation_handler = create_admin_handler(
            admin_functions=admin_functions,
            message_handler=self.show_operation_result
        )
        
        # UI references (extracted from gui_setup)
        self.screen_info = self.gui_setup['screen_info']
        self.time_manager = self.gui_setup['time_manager']
        self.font_sizes = self.gui_setup['font_sizes']
        self.padding_sizes = self.gui_setup['padding_sizes']
        
        # Convenience properties
        self.screen_width = self.screen_info['screen_width']
        self.screen_height = self.screen_info['screen_height']
        self.display_size = self.screen_info['display_size']
        self.is_square_display = self.screen_info['is_square_display']
        
        # UI variables
        self.time_string = self.time_manager['time_string']
        self.date_string = self.time_manager['date_string']
        self.status_text = self.gui_setup['status_manager']['status_var']
        
        # Colors (unchanged)
        self.colors = {
            'primary': '#2C3E50', 'secondary': '#34495E', 'accent': '#E74C3C',
            'success': '#27AE60', 'warning': '#F39C12', 'info': '#3498DB',
            'light': '#ECF0F1', 'dark': '#1A252F', 'gold': '#F1C40F', 'white': '#FFFFFF'
        }
        
        # Initialize based on authentication
        if skip_auth:
            self.auth_manager.authenticate_user(user_role)
            self.show_admin_panel()
        else:
            self.show_authentication_screen()
    
    # ========================================
    # AUTHENTICATION METHODS - Using AuthManager
    # ========================================
    
    def show_authentication_screen(self):
        """Show authentication screen using AuthenticationScreen component"""
        self.auth_screen = AuthenticationScreen(
            parent_root=self.root,
            colors=self.colors,
            font_sizes=self.font_sizes,
            on_success_callback=self.on_authentication_success
        )
        self.auth_screen.create_authentication_screen()
    
    def on_authentication_success(self, user_role):
        """Handle successful authentication
        
        Args:
            user_role: Authenticated user role
        """
        # Update auth manager
        self.auth_manager.authenticate_user(user_role)
        
        # Show admin panel
        self.show_admin_panel()
    
    # ========================================
    # MAIN INTERFACE METHODS - Using UI Components
    # ========================================
    
    def show_admin_panel(self):
        """Show the main admin panel interface"""
        # Clear window
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Main container
        main_container = tk.Frame(self.root, bg=self.colors['white'])
        main_container.pack(fill="both", expand=True,
                           padx=self.padding_sizes['content_x'],
                           pady=self.padding_sizes['content_y'])
        
        # Create interface based on display type
        if self.screen_info['is_wide_display']:
            self.create_wide_interface(main_container)
        else:
            self.create_standard_interface(main_container)
    
    def create_standard_interface(self, parent):
        """Create standard interface layout"""
        # Header
        self.create_header(parent)
        
        # Main content
        content_frame = tk.Frame(parent, bg=self.colors['white'])
        content_frame.pack(fill="both", expand=True, pady=self.padding_sizes['section_spacing'])
        
        # Menu cards
        self.create_menu_cards(content_frame)
    
    def create_wide_interface(self, parent):
        """Create wide display interface with sidebar"""
        # Header
        self.create_header(parent)
        
        # Main content with sidebar
        content_frame = tk.Frame(parent, bg=self.colors['white'])
        content_frame.pack(fill="both", expand=True, pady=self.padding_sizes['section_spacing'])
        
        # Sidebar for stats
        self.create_stats_sidebar(content_frame)
        
        # Menu cards in remaining space
        menu_frame = tk.Frame(content_frame, bg=self.colors['white'])
        menu_frame.pack(side="right", fill="both", expand=True)
        
        self.create_menu_cards(menu_frame)
    
    def create_header(self, parent):
        """Create header with role information"""
        header = tk.Frame(parent, bg=self.colors['primary'])
        header.pack(fill="x", pady=(0, self.padding_sizes['section_spacing']))
        
        # Title with role info
        role_name = self.auth_manager.get_role_display_name()
        title_text = f"🔐 Admin Control Center ({role_name})"
        
        tk.Label(header, text=title_text,
                font=("Arial", self.font_sizes['title'], "bold"),
                fg=self.colors['white'], bg=self.colors['primary']).pack(pady=10)
        
        # Time display
        time_frame = tk.Frame(header, bg=self.colors['primary'])
        time_frame.pack(pady=(0, 10))
        
        tk.Label(time_frame, textvariable=self.time_string,
                font=("Arial", self.font_sizes['time'], "bold"),
                fg=self.colors['gold'], bg=self.colors['primary']).pack()
        
        tk.Label(time_frame, textvariable=self.date_string,
                font=("Arial", self.font_sizes['date']),
                fg=self.colors['light'], bg=self.colors['primary']).pack()
    
    def create_menu_cards(self, parent):
        """Create menu cards using UIComponents with access control"""
        # Define all possible cards - FIX: Use the correct method calls
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
        
        # Filter cards based on user access
        accessible_cards = [
            card for card in all_cards_data
            if self.auth_manager.has_access(card[5])  # card[5] is function_name
        ]
        
        # Use UIComponents for layout
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
    # BUSINESS OPERATION METHODS - Add the missing methods!
    # ========================================
    
    def enroll_user(self):
        """Enroll new user - call admin operation"""
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
        """View users - call existing method"""
        self.show_users_window()
    
    def delete_user(self):
        """Delete user - call admin operation"""
        if not self.auth_manager.require_access("delete_fingerprint"):
            return
        
        result = messagebox.askquestion("Delete User", 
                                   "This will delete a user's fingerprint.\n\n" +
                                   "The deletion process will guide you through selecting the user.\n\n" +
                                   "Continue?")
        if result == 'yes':
            self.operation_handler.execute_operation('delete_user')
    
    def sync_database(self):
        """Sync database - call admin operation"""
        if not self.auth_manager.require_access("sync"):
            return
        
        result = messagebox.askquestion("Sync Database", 
                                   "This will synchronize with Google Sheets database.\n\n" +
                                   "This may take a few moments.\n\n" +
                                   "Continue?")
        if result == 'yes':
            self.operation_handler.execute_operation('sync_database')
    
    def view_time_records(self):
        """View time records - call existing method"""
        self.show_time_records_window()
    
    def clear_time_records(self):
        """Clear time records - call admin operation"""
        if not self.auth_manager.require_access("clear_records"):
            return
        
        result = messagebox.askquestion("Clear Time Records", 
                                   "This will DELETE ALL time records permanently.\n\n" +
                                   "⚠️ This action cannot be undone!\n\n" +
                                   "Continue?")
        if result == 'yes':
            self.operation_handler.execute_operation('clear_time_records')
    
    def create_stats_sidebar(self, parent):
        """Create statistics sidebar using UIComponents"""
        # Get stats from operation handler
        stats = self.operation_handler.get_stats_sync()
        
        # Responsive sidebar width
        sidebar_width = max(200, int(self.screen_width * 0.20))
        sidebar = tk.Frame(parent, bg=self.colors['secondary'], width=sidebar_width)
        sidebar.pack(side="left", fill="y", padx=(15, 15), pady=15)
        sidebar.pack_propagate(False)
        
        # Title
        tk.Label(sidebar, text="📊 LIVE STATISTICS",
                font=("Arial", self.font_sizes['title']), fg=self.colors['white'],
                bg=self.colors['secondary']).pack(pady=15)
        
        # Stat cards using UIComponents
        card_spacing = max(8, int(self.screen_height / 80))
        
        UIComponents.create_stat_card(sidebar, "👥", "Total Users",
                                    stats.get('total_students', 0) + stats.get('total_staff', 0),
                                    self.colors['info'], self.colors, self.display_size, card_spacing)
        
        UIComponents.create_stat_card(sidebar, "🎓", "Students",
                                    stats.get('total_students', 0),
                                    self.colors['success'], self.colors, self.display_size, card_spacing)
        
        UIComponents.create_stat_card(sidebar, "👔", "Staff",
                                    stats.get('total_staff', 0),
                                    self.colors['warning'], self.colors, self.display_size, card_spacing)
        
        UIComponents.create_stat_card(sidebar, "🚗", "Currently Inside",
                                    stats.get('users_currently_in', 0),
                                    self.colors['accent'], self.colors, self.display_size, card_spacing)
    
    # ========================================
    # BUSINESS OPERATION METHODS - Using AdminOperationHandler
    # ========================================
    
    def execute_admin_operation(self, operation_name):
        """Execute admin operation using operation handler
        
        Args:
            operation_name: Name of operation to execute
        """
        # Check access first
        if not self.auth_manager.require_access(operation_name.replace('_', '')):
            return
        
        # Check if operation is already running
        if self.operation_handler.is_busy(operation_name):
            messagebox.showwarning("Operation in Progress",
                                 f"The {operation_name.replace('_', ' ')} operation is already running.")
            return
        
        # Execute the operation
        self.operation_handler.execute_operation(operation_name)
    
    def show_operation_result(self, title, message, is_error=False):
        """Show operation result to user
        
        Args:
            title: Result title
            message: Result message
            is_error: Whether this is an error
        """
        if is_error:
            messagebox.showerror(title, message)
        else:
            messagebox.showinfo(title, message)
    
    # ========================================
    # WINDOW DISPLAY METHODS - Using Window Management
    # ========================================
    
    def show_users_window(self):
        """Show users window using WindowManager"""
        if not self.auth_manager.require_access("view_users"):
            return
        
        # Get users data
        users_data = self.operation_handler.get_users_sync()
        
        # Create modal window
        window_sizes = ResponsiveCalculator.get_window_sizes(self.screen_info, 'large_modal')
        users_window = WindowManager.setup_modal_window(
            parent=self.root,
            title="Enrolled Users",
            width=window_sizes['width'],
            height=window_sizes['height'],
            bg_color=self.colors['white']
        )
        
        # Header
        header = tk.Frame(users_window, bg=self.colors['primary'],
                         height=max(60, int(window_sizes['height'] * 0.12)))
        header.pack(fill="x")
        header.pack_propagate(False)
        
        tk.Label(header, text="👥 ENROLLED USERS",
                font=("Arial", self.font_sizes['title']), fg=self.colors['white'],
                bg=self.colors['primary']).pack(expand=True)
        
        # Content using UIComponents
        if not users_data:
            # Empty state
            empty_frame = tk.Frame(users_window, bg=self.colors['white'])
            empty_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            tk.Label(empty_frame, text="📭", font=("Arial", 32),
                    fg=self.colors['light'], bg=self.colors['white']).pack(pady=(50, 20))
            tk.Label(empty_frame, text="No users enrolled",
                    font=("Arial", self.font_sizes['subtitle']), fg=self.colors['secondary'],
                    bg=self.colors['white']).pack()
        else:
            # User list using scrollable container
            scrollable_frame = UIComponents.create_scrollable_container(users_window, self.colors)
            
            # Create user cards
            for slot_id, info in sorted(users_data.items(), key=lambda x: x[0]):
                if slot_id == "1":  # Skip admin
                    continue
                UIComponents.create_modern_user_card(scrollable_frame, slot_id, info,
                                                   self.colors, self.display_size)
        
        # Close button
        close_btn = tk.Button(users_window, text="CLOSE",
                             font=("Arial", self.font_sizes['button'], "bold"),
                             bg=self.colors['accent'], fg=self.colors['white'],
                             relief='flat', bd=0, cursor="hand2",
                             padx=30, pady=10, command=users_window.destroy)
        close_btn.pack(pady=15)
    
    def show_time_records_window(self):
        """Show time records window"""
        if not self.auth_manager.require_access("get_time_records"):
            return
        
        # Get time records (this will be async in the background)
        self.operation_handler.execute_operation("get_time_records",
                                               callback=self._display_time_records)
    
    def _display_time_records(self, result):
        """Display time records in a window
        
        Args:
            result: Result from get_time_records operation
        """
        if not result['success']:
            return  # Error already shown by operation handler
        
        records = result['data']
        
        # Create modal window
        window_sizes = ResponsiveCalculator.get_window_sizes(self.screen_info, 'large_modal')
        records_window = WindowManager.setup_modal_window(
            parent=self.root,
            title="Time Records",
            width=window_sizes['width'],
            height=window_sizes['height'],
            bg_color=self.colors['white']
        )
        
        # Header
        header = tk.Frame(records_window, bg=self.colors['primary'],
                         height=max(60, int(window_sizes['height'] * 0.12)))
        header.pack(fill="x")
        header.pack_propagate(False)
        
        tk.Label(header, text="🕒 TIME RECORDS",
                font=("Arial", self.font_sizes['title']), fg=self.colors['white'],
                bg=self.colors['primary']).pack(expand=True)
        
        if not records:
            # Empty state
            empty_frame = tk.Frame(records_window, bg=self.colors['white'])
            empty_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            tk.Label(empty_frame, text="📭", font=("Arial", 32),
                    fg=self.colors['light'], bg=self.colors['white']).pack(pady=(50, 20))
            tk.Label(empty_frame, text="No time records found",
                    font=("Arial", self.font_sizes['subtitle']), fg=self.colors['secondary'],
                    bg=self.colors['white']).pack()
        else:
            # Records table
            self._create_records_table(records_window, records)
        
        # Close button
        close_btn = tk.Button(records_window, text="CLOSE",
                             font=("Arial", self.font_sizes['button'], "bold"),
                             bg=self.colors['accent'], fg=self.colors['white'],
                             relief='flat', bd=0, cursor="hand2",
                             padx=30, pady=10, command=records_window.destroy)
        close_btn.pack(pady=15)
    
    def _create_records_table(self, parent, records):
        """Create records table using ttk.Treeview
        
        Args:
            parent: Parent widget
            records: List of time records
        """
        table_frame = tk.Frame(parent, bg=self.colors['white'])
        table_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Treeview',
                       background=self.colors['white'],
                       fieldbackground=self.colors['white'],
                       borderwidth=0,
                       font=('Arial', max(8, int(self.display_size / 100))))
        
        # Create treeview
        columns = ('Date', 'Time', 'ID', 'Name', 'Type', 'Status')
        tree = ttk.Treeview(table_frame, columns=columns, show='tree headings',
                           height=max(15, int(self.screen_height / 30)))
        
        # Configure columns
        tree.column('#0', width=0, stretch=False)
        for col in columns:
            tree.column(col, width=max(80, int(self.screen_width / 12)))
            tree.heading(col, text=col)
        
        # Add records
        for i, record in enumerate(records):
            values = (
                record.get('date', 'N/A'),
                record.get('time', 'N/A'),
                record.get('student_id', 'N/A'),
                record.get('student_name', 'N/A'),
                record.get('user_type', 'STUDENT'),
                record.get('status', 'N/A')
            )
            tree.insert('', 'end', values=values)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def show_office_management(self):
        """Show office management window using UIComponents"""
        if not self.auth_manager.require_access("system_maintenance"):
            return
        
        # Create modal window using WindowManager
        window_sizes = ResponsiveCalculator.get_window_sizes(self.screen_info, 'large_modal')
        office_window = WindowManager.setup_modal_window(
            parent=self.root,
            title="Office Management",
            width=window_sizes['width'],
            height=window_sizes['height'],
            bg_color=self.colors['white']
        )
        
        # Header
        header = tk.Frame(office_window, bg=self.colors['primary'],
                         height=max(60, int(window_sizes['height'] * 0.12)))
        header.pack(fill="x")
        header.pack_propagate(False)
        
        tk.Label(header, text="🏢 Office Management & Security Code Configuration",
                font=("Arial", self.font_sizes['subtitle']), fg=self.colors['light'],
                bg=self.colors['primary']).pack(expand=True)
        
        # Use UIComponents for scrollable content
        scrollable_frame = UIComponents.create_scrollable_container(office_window, self.colors)
        
        # Use UIComponents for complete office management section
        office_section = tk.Frame(scrollable_frame, bg=self.colors['white'])
        office_section.pack(fill="x", padx=15, pady=15)
        
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
    
    # ========================================
    # MAIN CONTROL METHODS - No Changes Needed
    # ========================================
    
    def run(self):
        """Run the GUI"""
        try:
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


# Backward compatibility alias
AdminPanelGUI = AdminPanelView

# For compatibility with existing imports
class AdminPanelGUI(AdminPanelView):
    """Backward compatibility class - same as AdminPanelView"""
    pass
