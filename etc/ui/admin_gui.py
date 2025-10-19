# ui/admin_gui.py - Complete Fixed Admin Panel GUI with Office Management - RESPONSIVE for 1024x768

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import threading
from datetime import datetime
import time 
import os
from PIL import Image, ImageTk
import json

class AdminPanelGUI:
    def __init__(self, admin_functions, skip_auth=False, user_role="super_admin"):
        self.root = tk.Tk()
        self.admin_functions = admin_functions
        self.authenticated = skip_auth
        self.user_role = user_role
        
        # Get screen dimensions and detect display type
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        
        # Calculate aspect ratio to determine display type
        aspect_ratio = self.screen_width / self.screen_height
        self.is_square_display = abs(aspect_ratio - 1.0) < 0.3  # Within 30% of square (for 1024x768)
        self.is_wide_display = aspect_ratio > 1.5  # Wider than 3:2
        
        # Set base size for responsive calculations
        if self.is_square_display:
            self.display_size = min(self.screen_width, self.screen_height)
        else:
            self.display_size = min(self.screen_width, self.screen_height)
        
        self.colors = {
            'primary': '#2C3E50',      # Dark blue-gray
            'secondary': '#34495E',     # Lighter blue-gray
            'accent': '#E74C3C',        # Red accent
            'success': '#27AE60',       # Green
            'warning': '#F39C12',       # Orange
            'info': '#3498DB',          # Blue
            'light': '#ECF0F1',         # Light gray
            'dark': '#1A252F',          # Very dark
            'gold': '#F1C40F',          # Gold
            'white': '#FFFFFF'
        }
        
        self.setup_window()
        self.create_variables()
        
        if skip_auth:
            self.show_admin_panel()
        else:
            self.create_authentication_screen()
            
    def has_access(self, function_name):
        """Check if current user role has access to a function"""
        if self.user_role == "super_admin":
            return True
        elif self.user_role == "guard":
            # Guard can only access enroll and sync
            allowed_functions = ["enroll", "sync"]
            return function_name in allowed_functions
        return False
        
    # Menu Action Functions
    def enroll_user(self):
        """Enroll new user - SIMPLE FIX"""
        result = messagebox.askquestion("Enroll User", 
                                   "This will start the enrollment process.\n\n" +
                                   "You will need:\n" +
                                   "• Student/Staff ID\n" +
                                   "• User's fingerprint\n\n" +
                                   "Continue?",
                                   icon='info')
        if result == 'yes':
            # Show loading message
            messagebox.showinfo("Enrollment Started", 
                          "Enrollment process starting...\n\n" +
                          "Please check the terminal for instructions.",
                          icon='info')
        
            # Run enrollment in background without complex threading
            try:
                self.admin_functions['enroll']()
            except Exception as e:
                messagebox.showerror("Enrollment Error", 
                               f"Enrollment failed:\n\n{str(e)}",
                               icon='error')
    
    def view_users(self):
        """View enrolled users"""
        thread = threading.Thread(target=self.load_and_display_users, daemon=True)
        thread.start()
    
    def load_and_display_users(self):
        """Load and display users in a new window"""
        try:
            # Load fingerprint database
            database_path = "json_folder/fingerprint_database.json"
            if os.path.exists(database_path):
                with open(database_path, 'r') as f:
                    database = json.load(f)
            else:
                database = {}
            
            self.root.after(0, lambda: self.display_users_window(database))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to load users: {str(e)}"))
    
    def display_users_window(self, database):
        """Display users in a modern window - RESPONSIVE"""
        # Create new window with responsive sizing
        users_window = tk.Toplevel(self.root)
        users_window.title("Enrolled Users Database")
        
        # Responsive window sizing
        if self.is_square_display:
            window_width = int(self.screen_width * 0.85)
            window_height = int(self.screen_height * 0.80)
        else:
            window_width = int(self.screen_width * 0.80)
            window_height = int(self.screen_height * 0.85)
            
        # Center window
        x = (self.screen_width - window_width) // 2
        y = (self.screen_height - window_height) // 2
        users_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        users_window.configure(bg=self.colors['light'])
        
        # Responsive font sizes
        header_font_size = max(16, int(self.display_size / 50))
        
        # Header
        header_height = max(60, int(window_height * 0.10))
        header = tk.Frame(users_window, bg=self.colors['primary'], height=header_height)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        tk.Label(header, text="👥 ENROLLED USERS DATABASE", 
                font=("Arial", header_font_size, "bold"), fg=self.colors['white'], 
                bg=self.colors['primary']).pack(expand=True)
        
        # Stats bar
        stats_bar = tk.Frame(users_window, bg=self.colors['secondary'])
        stats_bar.pack(fill="x")
        
        student_count = sum(1 for info in database.values() if info.get('user_type') == 'STUDENT')
        staff_count = sum(1 for info in database.values() if info.get('user_type') == 'STAFF')
        
        stats_content = tk.Frame(stats_bar, bg=self.colors['secondary'])
        stats_content.pack(pady=10)
        
        # Responsive stats layout
        stats_font_size = max(8, int(self.display_size / 80))
        stats_number_size = max(14, int(self.display_size / 50))
        
        for label, value, color in [
            ("Total Users", len(database) - 1, self.colors['gold']),  # -1 to exclude admin
            ("Students", student_count, self.colors['success']),
            ("Staff", staff_count, self.colors['info'])
        ]:
            stat_item = tk.Frame(stats_content, bg=self.colors['secondary'])
            stat_item.pack(side="left", padx=20 if self.is_square_display else 30)
            tk.Label(stat_item, text=label, font=("Arial", stats_font_size), 
                    fg=self.colors['light'], bg=self.colors['secondary']).pack()
            tk.Label(stat_item, text=str(value), font=("Arial", stats_number_size, "bold"), 
                    fg=color, bg=self.colors['secondary']).pack()
        
        # Create scrollable frame
        container = tk.Frame(users_window, bg=self.colors['white'])
        container.pack(fill="both", expand=True, padx=15, pady=15)
        
        canvas = tk.Canvas(container, bg=self.colors['white'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['white'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Bind mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        # Bind keyboard arrow keys for scrolling
        def _on_key_press(event):
            if event.keysym == 'Up':
                canvas.yview_scroll(-3, "units")
            elif event.keysym == 'Down':
                canvas.yview_scroll(3, "units")
            elif event.keysym == 'Page_Up':
                canvas.yview_scroll(-10, "units")
            elif event.keysym == 'Page_Down':
                canvas.yview_scroll(10, "units")
        
        # Bind events
        canvas.bind("<MouseWheel>", _on_mousewheel)
        container.bind("<MouseWheel>", _on_mousewheel)
        users_window.bind("<MouseWheel>", _on_mousewheel)
        
        # Make window focusable and bind arrow keys
        users_window.focus_set()
        users_window.bind("<Key>", _on_key_press)
        users_window.bind("<Up>", _on_key_press)
        users_window.bind("<Down>", _on_key_press)
        users_window.bind("<Page_Up>", _on_key_press)
        users_window.bind("<Page_Down>", _on_key_press)
        
        # User cards
        for slot_id, info in sorted(database.items(), key=lambda x: x[0]):
            if slot_id == "1":  # Skip admin
                continue
            self.create_modern_user_card(scrollable_frame, slot_id, info)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Update scroll region after adding all cards
        users_window.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))
        
        # Close button - responsive
        close_btn_size = max(10, int(self.display_size / 70))
        close_btn = tk.Button(users_window, text="CLOSE", 
                             font=("Arial", close_btn_size, "bold"), 
                             bg=self.colors['accent'], fg=self.colors['white'],
                             relief='flat', bd=0, cursor="hand2",
                             padx=30, pady=10, command=users_window.destroy)
        close_btn.pack(pady=15)
    
    def create_modern_user_card(self, parent, slot_id, info):
        """Create a modern user information card - RESPONSIVE"""
        # Card container with shadow
        card_container = tk.Frame(parent, bg=self.colors['white'])
        card_container.pack(fill="x", padx=8, pady=6)
        
        # Card
        card = tk.Frame(card_container, bg=self.colors['light'], relief='flat', bd=0)
        card.pack(fill="x", padx=2, pady=2)
        
        # Type indicator
        type_color = self.colors['success'] if info.get('user_type') == 'STUDENT' else self.colors['info']
        type_bar = tk.Frame(card, bg=type_color, width=5)
        type_bar.pack(side="left", fill="y")
        
        # Content with responsive padding
        padding_x = max(15, int(self.display_size / 50))
        padding_y = max(10, int(self.display_size / 80))
        content = tk.Frame(card, bg=self.colors['light'])
        content.pack(side="left", fill="both", expand=True, padx=padding_x, pady=padding_y)
        
        # Header row
        header_row = tk.Frame(content, bg=self.colors['light'])
        header_row.pack(fill="x", pady=(0, 8))
        
        # Name and type - responsive fonts
        name_font_size = max(12, int(self.display_size / 70))
        type_font_size = max(8, int(self.display_size / 100))
        
        name_frame = tk.Frame(header_row, bg=self.colors['light'])
        name_frame.pack(side="left")
        
        tk.Label(name_frame, text=info.get('name', 'N/A'), 
                font=("Arial", name_font_size, "bold"), fg=self.colors['dark'], 
                bg=self.colors['light']).pack(anchor="w")
        
        type_text = f"{info.get('user_type', 'UNKNOWN')} • Slot #{slot_id}"
        tk.Label(name_frame, text=type_text, 
                font=("Arial", type_font_size), fg=type_color, 
                bg=self.colors['light']).pack(anchor="w")
        
        # Details grid
        details_frame = tk.Frame(content, bg=self.colors['light'])
        details_frame.pack(fill="x")
        
        # Create two columns
        col1 = tk.Frame(details_frame, bg=self.colors['light'])
        col1.pack(side="left", fill="both", expand=True)
        
        col2 = tk.Frame(details_frame, bg=self.colors['light'])
        col2.pack(side="left", fill="both", expand=True)
        
        # Column 1 details
        if info.get('user_type') == 'STUDENT':
            self.add_detail_row(col1, "ID:", info.get('student_id', 'N/A'))
            self.add_detail_row(col1, "Course:", info.get('course', 'N/A'))
        else:
            self.add_detail_row(col1, "ID:", info.get('staff_no', 'N/A'))
            self.add_detail_row(col1, "Role:", info.get('staff_role', 'N/A'))
        
        # Column 2 details
        self.add_detail_row(col2, "License:", info.get('license_number', 'N/A'))
        self.add_detail_row(col2, "Plate:", info.get('plate_number', 'N/A'))
    
    def add_detail_row(self, parent, label, value):
        """Add a detail row with responsive fonts"""
        row = tk.Frame(parent, bg=self.colors['light'])
        row.pack(fill="x", pady=1)
        
        detail_font_size = max(8, int(self.display_size / 100))
        
        tk.Label(row, text=label, font=("Arial", detail_font_size), 
                fg=self.colors['secondary'], bg=self.colors['light'], 
                width=8, anchor="w").pack(side="left")
        tk.Label(row, text=value, font=("Arial", detail_font_size, "bold"), 
                fg=self.colors['dark'], bg=self.colors['light']).pack(side="left")
    
    def delete_user(self):
        """Delete user fingerprint - FIXED"""
        slot_id = simpledialog.askstring("Delete User", 
                                       "Enter Slot ID to delete:",
                                       parent=self.root)
        
        if slot_id:
            if slot_id == "1":
                messagebox.showerror("Error", "Cannot delete admin slot!")
                return
            
            if messagebox.askyesno("Confirm Delete", 
                                 f"Delete user at slot #{slot_id}?\n\nThis cannot be undone!",
                                 icon='warning'):
                thread = threading.Thread(target=lambda: self.run_delete(slot_id), daemon=True)
                thread.start()
    
    def run_delete(self, slot_id):
        """Run delete operation"""
        try:
            # Call delete function with slot_id
            self.admin_functions['delete_fingerprint'](slot_id)
            self.root.after(0, lambda: messagebox.showinfo("Success", 
                                                          f"User at slot #{slot_id} deleted successfully!",
                                                          icon='info'))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Delete failed: {str(e)}"))
    
    def sync_database(self):
        """Sync database from Google Sheets"""
        result = messagebox.askyesno("Sync Database", 
                                    "Sync student/staff data from Google Sheets?\n\n" +
                                    "This will update the database with latest registrations.",
                                    icon='question')
        if result:
            thread = threading.Thread(target=lambda: self.run_function('sync'), daemon=True)
            thread.start()
    
    def view_time_records(self):
        """View time records"""
        thread = threading.Thread(target=self.load_and_display_time_records, daemon=True)
        thread.start()
    
    def load_and_display_time_records(self):
        """Load and display time records"""
        try:
            records = self.admin_functions['get_time_records']()
            self.root.after(0, lambda: self.display_time_records_window(records))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to load records: {str(e)}"))
    
    def display_time_records_window(self, records):
            """Display time records in a modern window - RESPONSIVE"""
            # Create new window with responsive sizing
            records_window = tk.Toplevel(self.root)
            records_window.title("Time Records")

            # Responsive window sizing
            if self.is_square_display:
                window_width = int(self.screen_width * 0.80)
                window_height = int(self.screen_height * 0.75)
            else:
                window_width = int(self.screen_width * 0.75)
                window_height = int(self.screen_height * 0.80)

            # Center window
            x = (self.screen_width - window_width) // 2
            y = (self.screen_height - window_height) // 2
            records_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
            records_window.configure(bg=self.colors['light'])

            # Responsive header
            header_font_size = max(16, int(self.display_size / 50))
            header_height = max(60, int(window_height * 0.10))
            header = tk.Frame(records_window, bg=self.colors['primary'], height=header_height)
            header.pack(fill="x")
            header.pack_propagate(False)

            tk.Label(header, text="🕒 TIME RECORDS",
                    font=("Arial", header_font_size, "bold"), fg=self.colors['white'],
                    bg=self.colors['primary']).pack(expand=True)

            if not records:
                # Empty state
                empty_frame = tk.Frame(records_window, bg=self.colors['white'])
                empty_frame.pack(fill="both", expand=True, padx=20, pady=20)

                empty_icon_size = max(32, int(self.display_size / 25))
                empty_text_size = max(12, int(self.display_size / 65))

                tk.Label(empty_frame, text="📭", font=("Arial", empty_icon_size),
                        fg=self.colors['light'], bg=self.colors['white']).pack(pady=(50, 20))
                tk.Label(empty_frame, text="No time records found",
                        font=("Arial", empty_text_size), fg=self.colors['secondary'],
                        bg=self.colors['white']).pack()
            else:
                # Create modern table
                table_frame = tk.Frame(records_window, bg=self.colors['white'])
                table_frame.pack(fill="both", expand=True, padx=15, pady=15)

                # Configure style
                style = ttk.Style()
                style.theme_use('clam')
                style.configure('Treeview',
                              background=self.colors['white'],
                              fieldbackground=self.colors['white'],
                              borderwidth=0,
                              font=('Arial', max(8, int(self.display_size / 100))))
                style.configure('Treeview.Heading',
                              background=self.colors['light'],
                              font=('Arial', max(9, int(self.display_size / 90)), 'bold'))
                style.map('Treeview', background=[('selected', self.colors['info'])])

                # Create treeview with responsive height
                tree_height = max(15, int(window_height / 30))
                tree = ttk.Treeview(table_frame,
                                   columns=('Date', 'Time', 'ID', 'Name', 'Type', 'Status'),
                                   show='tree headings', height=tree_height)

                # Configure columns with responsive widths
                base_width = max(80, int(window_width / 10))
                tree.column('#0', width=0, stretch=False)
                tree.column('Date', width=base_width)
                tree.column('Time', width=int(base_width * 0.8))
                tree.column('ID', width=base_width)
                tree.column('Name', width=int(base_width * 1.8))
                tree.column('Type', width=int(base_width * 0.8))
                tree.column('Status', width=int(base_width * 0.6))

                # Configure headings
                for col in ['Date', 'Time', 'ID', 'Name', 'Type', 'Status']:
                    tree.heading(col, text=col)

                # Add records with alternating colors
                for i, record in enumerate(records):
                    # --- START OF THE FIX ---
                    user_type = record.get('user_type', 'STUDENT')
                    if user_type == 'GUEST':
                        user_type = 'VISITOR'  # Change the label here
                    # --- END OF THE FIX ---

                    values = (
                        record.get('date', 'N/A'),
                        record.get('time', 'N/A'),
                        record.get('student_id', 'N/A'),
                        record.get('student_name', 'N/A'),
                        user_type, # Use the modified user_type
                        record.get('status', 'N/A')
                    )

                    tag = 'even' if i % 2 == 0 else 'odd'
                    status_tag = 'in' if record.get('status') == 'IN' else 'out'
                    tree.insert('', 'end', values=values, tags=(tag, status_tag))

                # Configure tags
                tree.tag_configure('even', background=self.colors['light'])
                tree.tag_configure('odd', background=self.colors['white'])
                tree.tag_configure('in', foreground=self.colors['success'])
                tree.tag_configure('out', foreground=self.colors['accent'])

                # Scrollbar
                scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=tree.yview)
                tree.configure(yscrollcommand=scrollbar.set)

                tree.pack(side='left', fill='both', expand=True)
                scrollbar.pack(side='right', fill='y')

            # Close button - responsive
            close_btn_size = max(10, int(self.display_size / 70))
            close_btn = tk.Button(records_window, text="CLOSE",
                                 font=("Arial", close_btn_size, "bold"),
                                 bg=self.colors['accent'], fg=self.colors['white'],
                                 relief='flat', bd=0, cursor="hand2",
                                 padx=30, pady=10, command=records_window.destroy)
            close_btn.pack(pady=15)
        
    def clear_time_records(self):
        """Clear all time records - FIXED"""
        # Custom confirmation dialog
        if messagebox.askyesno("Clear Records", 
                              "Delete ALL time records?\n\n" +
                              "This will permanently remove all attendance data!",
                              icon='warning'):
            # Double confirmation
            if messagebox.askyesno("Final Confirmation", 
                                 "Are you ABSOLUTELY SURE?\n\n" +
                                 "All time records will be deleted permanently!",
                                 icon='warning'):
                # FIXED: Call the function directly instead of through run_function
                try:
                    # Import the function directly
                    from database.db_operations import clear_all_time_records
                    
                    if clear_all_time_records():
                        messagebox.showinfo("✅ Success", 
                                          "All time records have been cleared successfully!",
                                          icon='info')
                    else:
                        messagebox.showerror("❌ Error", 
                                           "Failed to clear records. Please try again.",
                                           icon='error')
                except Exception as e:
                    messagebox.showerror("❌ Error", 
                                       f"Failed to clear records:\n\n{str(e)}",
                                       icon='error')
    
    def open_dashboard(self):
        """Open web dashboard"""
        import webbrowser
        try:
            webbrowser.open("http://localhost:5000")
            messagebox.showinfo("Dashboard Opened", 
                              "Web dashboard opened in your browser!\n\n" +
                              "Default login: admin / motorpass123",
                              icon='info')
        except:
            messagebox.showerror("Error", "Failed to open web dashboard")
    
    def exit_system(self):
        """Exit the system"""
        if messagebox.askyesno("Exit Admin Panel", 
                              "Exit the admin panel?\n\n" +
                              "You will return to the main menu.",
                              icon='question'):
            self.close()
    
    def show_office_management(self):
        """Show office management window - RESPONSIVE"""
        # Create office management window with responsive sizing
        office_window = tk.Toplevel(self.root)
        office_window.title("System Maintenance - Office Management")
        
        # Responsive window sizing
        if self.is_square_display:
            window_width = int(self.screen_width * 0.75)
            window_height = int(self.screen_height * 0.70)
        else:
            window_width = int(self.screen_width * 0.60)
            window_height = int(self.screen_height * 0.75)
            
        office_window.configure(bg=self.colors['white'])
        
        # Center window
        x = (self.screen_width - window_width) // 2
        y = (self.screen_height - window_height) // 2
        office_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Responsive header
        header_font_size = max(16, int(self.display_size / 50))
        subtitle_font_size = max(9, int(self.display_size / 90))
        header_height = max(70, int(window_height * 0.12))
        
        header = tk.Frame(office_window, bg=self.colors['primary'], height=header_height)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        header_content = tk.Frame(header, bg=self.colors['primary'])
        header_content.pack(expand=True)
        
        tk.Label(header_content, text="🏢 SYSTEM MAINTENANCE", 
                font=("Arial", header_font_size, "bold"), fg=self.colors['white'], 
                bg=self.colors['primary']).pack(pady=(10, 5))
        
        tk.Label(header_content, text="Office Management & Security Code Configuration", 
                font=("Arial", subtitle_font_size), fg=self.colors['light'], 
                bg=self.colors['primary']).pack()
        
        # Content
        content = tk.Frame(office_window, bg=self.colors['white'])
        content.pack(fill="both", expand=True)
        
        # Add office management section
        self.create_office_management_section(content)
        
        # Footer with close button - responsive
        footer_height = max(50, int(window_height * 0.08))
        footer = tk.Frame(office_window, bg=self.colors['light'], height=footer_height)
        footer.pack(fill="x")
        footer.pack_propagate(False)
        
        close_btn_size = max(10, int(self.display_size / 70))
        close_btn = tk.Button(footer, text="✅ CLOSE", 
                             font=("Arial", close_btn_size, "bold"), 
                             bg=self.colors['accent'], fg=self.colors['white'],
                             relief='flat', bd=0, cursor="hand2",
                             padx=30, pady=8, command=office_window.destroy)
        close_btn.pack(pady=10)

    def create_office_management_section(self, parent):
            """Add office management to admin panel - RESPONSIVE with 4-digit codes and rotation"""
            try:
                from database.office_operation import get_all_offices, add_office, update_office_code, delete_office
            except ImportError:
                # Show error if office operations not available
                error_frame = tk.Frame(parent, bg=self.colors['white'])
                error_frame.pack(fill="x", padx=10, pady=5)
                error_font_size = max(10, int(self.display_size / 80))
                tk.Label(error_frame, text="⚠️ Office Management System Not Available", 
                        font=("Arial", error_font_size, "bold"), fg=self.colors['accent'], 
                        bg=self.colors['white']).pack(pady=20)
                return
            
            # FIRST: Ensure the offices table exists
            try:
                from database.office_operation import create_office_table
                create_office_table()  # This will create the table if it doesn't exist
            except Exception as e:
                print(f"❌ Error creating office table: {e}")
            
            # Responsive fonts
            section_font_size = max(10, int(self.display_size / 80))
            instruction_font_size = max(8, int(self.display_size / 100))
            button_font_size = max(8, int(self.display_size / 110))
            
            # Office Management Frame
            office_frame = tk.LabelFrame(parent, text="🏢 Office Management & Security Codes", 
                                        font=("Arial", section_font_size, "bold"), 
                                        bg=self.colors['white'], fg=self.colors['primary'],
                                        relief="ridge", bd=2)
            office_frame.pack(fill="x", padx=8, pady=4)
            
            # Instructions - UPDATED TO 4-DIGIT
            instruction_label = tk.Label(office_frame, 
                                        text="Manage visitor offices and their 4-digit security codes for timeout verification",
                                        font=("Arial", instruction_font_size), fg=self.colors['secondary'],
                                        bg=self.colors['white'])
            instruction_label.pack(pady=(8, 0))
            
            # Office list with scrollbar - responsive height
            list_frame = tk.Frame(office_frame, bg=self.colors['white'])
            list_frame.pack(fill="both", expand=True, padx=8, pady=8)
            
            list_height = max(6, int(self.display_size / 120))
            offices_list = tk.Listbox(list_frame, height=list_height, font=("Arial", instruction_font_size))
            scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=offices_list.yview)
            offices_list.configure(yscrollcommand=scrollbar.set)
            
            offices_list.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            def refresh_office_list():
                """Refresh the office list display"""
                offices_list.delete(0, tk.END)
                offices = get_all_offices()
                for office in offices:
                    offices_list.insert(tk.END, f"{office['office_name']} (Code: {office['office_code']})")
            
            # Buttons frame
            btn_frame = tk.Frame(office_frame, bg=self.colors['white'])
            btn_frame.pack(fill="x", padx=8, pady=(0, 8))
            
            def add_new_office():
                """Add a new office with auto-generated 4-digit code"""
                office_name = simpledialog.askstring("Add Office", "Enter office name:")
                if office_name and office_name.strip():
                    if add_office(office_name.strip()):
                        # UPDATED MESSAGE TO 4-DIGIT
                        messagebox.showinfo("Success", f"Office '{office_name}' added successfully!\nA unique 4-digit code has been generated.")
                        refresh_office_list()
                    else:
                        messagebox.showerror("Error", "Failed to add office!")
            
            def update_office_code_gui():
                """Update the security code for selected office"""
                selection = offices_list.curselection()
                if not selection:
                    messagebox.showwarning("Warning", "Please select an office first!")
                    return
                
                office_text = offices_list.get(selection[0])
                office_name = office_text.split(" (Code:")[0]
                current_code = office_text.split("Code: ")[1].replace(")", "")
                
                # UPDATED DIALOG TO 4-DIGIT
                new_code = simpledialog.askstring("Update Security Code", 
                                                 f"Current code for '{office_name}': {current_code}\n\nEnter new 4-digit code:")
                if new_code and new_code.strip():
                    if update_office_code(office_name, new_code.strip()):
                        messagebox.showinfo("Success", f"Security code updated for '{office_name}'!")
                        refresh_office_list()
                    else:
                        # UPDATED ERROR MESSAGE TO 4-DIGIT
                        messagebox.showerror("Error", "Failed to update code! Make sure it's exactly 4 digits and not already in use.")
            
            def delete_office_gui():
                """Delete (deactivate) the selected office"""
                selection = offices_list.curselection()
                if not selection:
                    messagebox.showwarning("Warning", "Please select an office first!")
                    return
                
                office_text = offices_list.get(selection[0])
                office_name = office_text.split(" (Code:")[0]
                
                if messagebox.askyesno("Confirm Delete", 
                                      f"Delete office '{office_name}'?\n\nThis will:\n• Remove the office from visitor selection\n• Disable its security code\n• This action cannot be undone!"):
                    if delete_office(office_name):
                        messagebox.showinfo("Success", f"Office '{office_name}' deleted!")
                        refresh_office_list()
                    else:
                        messagebox.showerror("Error", "Failed to delete office!")
            
            def show_office_codes():
                """Show all office codes for reference"""
                offices = get_all_offices()
                if not offices:
                    messagebox.showinfo("No Offices", "No offices found in the system.")
                    return
                
                codes_text = "🏢 OFFICE SECURITY CODES:\n" + "="*40 + "\n"
                for office in offices:
                    codes_text += f"• {office['office_name']}: {office['office_code']}\n"
                
                # UPDATED MESSAGE TO 4-DIGIT
                codes_text += "\n⚠️ These 4-digit codes are used for secure guest timeout verification."
                
                # Create a window to display codes - responsive
                codes_window = tk.Toplevel(self.root)
                codes_window.title("Office Security Codes")
                
                # Responsive sizing
                codes_width = int(self.display_size * 0.4)
                codes_height = int(self.display_size * 0.35)
                codes_window.geometry(f"{codes_width}x{codes_height}")
                codes_window.configure(bg=self.colors['white'])
                
                # Center window
                codes_window.update_idletasks()
                x = (codes_window.winfo_screenwidth() // 2) - (codes_width // 2)
                y = (codes_window.winfo_screenheight() // 2) - (codes_height // 2)
                codes_window.geometry(f"{codes_width}x{codes_height}+{x}+{y}")
                
                # Text widget with scrollbar
                text_frame = tk.Frame(codes_window, bg=self.colors['white'])
                text_frame.pack(fill="both", expand=True, padx=15, pady=15)
                
                text_font_size = max(9, int(self.display_size / 90))
                text_widget = tk.Text(text_frame, font=("Courier", text_font_size), wrap="word")
                text_scrollbar = tk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview)
                text_widget.configure(yscrollcommand=text_scrollbar.set)
                
                text_widget.insert("1.0", codes_text)
                text_widget.config(state="disabled")  # Make read-only
                
                text_widget.pack(side="left", fill="both", expand=True)
                text_scrollbar.pack(side="right", fill="y")
                
                # Close button
                close_font_size = max(8, int(self.display_size / 100))
                tk.Button(codes_window, text="Close", command=codes_window.destroy,
                         bg=self.colors['primary'], fg="white", font=("Arial", close_font_size, "bold"),
                         cursor="hand2", pady=5).pack(pady=8)
            
            # Responsive button padding
            btn_padding = max(8, int(self.display_size / 100))
            
            # Buttons row 1
            btn_row1 = tk.Frame(btn_frame, bg=self.colors['white'])
            btn_row1.pack(fill="x", pady=(0, 4))
            
            tk.Button(btn_row1, text="➕ Add Office", command=add_new_office,
                     bg=self.colors['success'], fg="white", font=("Arial", button_font_size, "bold"),
                     cursor="hand2", padx=btn_padding, pady=4).pack(side="left", padx=3)
            
            tk.Button(btn_row1, text="🔄 Update Code", command=update_office_code_gui,
                     bg=self.colors['warning'], fg="white", font=("Arial", button_font_size, "bold"),
                     cursor="hand2", padx=btn_padding, pady=4).pack(side="left", padx=3)
            
            tk.Button(btn_row1, text="🗑️ Delete Office", command=delete_office_gui,
                     bg=self.colors['accent'], fg="white", font=("Arial", button_font_size, "bold"),
                     cursor="hand2", padx=btn_padding, pady=4).pack(side="left", padx=3)
            
            # Buttons row 2
            btn_row2 = tk.Frame(btn_frame, bg=self.colors['white'])
            btn_row2.pack(fill="x", pady=(0, 8))
            
            tk.Button(btn_row2, text="🔍 View All Codes", command=show_office_codes,
                     bg=self.colors['info'], fg="white", font=("Arial", button_font_size, "bold"),
                     cursor="hand2", padx=btn_padding, pady=4).pack(side="left", padx=3)
            
            tk.Button(btn_row2, text="🔄 Refresh List", command=refresh_office_list,
                     bg=self.colors['secondary'], fg="white", font=("Arial", button_font_size, "bold"),
                     cursor="hand2", padx=btn_padding, pady=4).pack(side="right", padx=3)
            
            # ROTATION MANAGEMENT SECTION (NEW)
            tk.Label(office_frame, text="", bg=self.colors['white']).pack(pady=5)  # Spacer
            
            rotation_label = tk.Label(office_frame, text="🔄 Code Rotation (System Maintenance)", 
                                     font=("Arial", section_font_size, "bold"), 
                                     bg=self.colors['white'], fg=self.colors['primary'])
            rotation_label.pack(pady=(10, 5))
            
            rotation_instruction = tk.Label(office_frame, 
                                           text="Rotate all office codes at once - codes automatically sync to Firebase",
                                           font=("Arial", instruction_font_size), fg=self.colors['secondary'],
                                           bg=self.colors['white'])
            rotation_instruction.pack(pady=(0, 10))
            
            # Rotation buttons frame
            rotation_btn_frame = tk.Frame(office_frame, bg=self.colors['white'])
            rotation_btn_frame.pack(fill="x", padx=8, pady=(0, 8))
            
            def weekly_rotation():
                """Weekly code rotation"""
                if messagebox.askyesno("Weekly Code Rotation", 
                                      "Rotate ALL office codes?\n\n" +
                                      "This will:\n" +
                                      "• Generate new 4-digit codes for all offices\n" +
                                      "• Sync codes to Firebase automatically\n" +
                                      "• Old codes will become invalid\n\n" +
                                      "Continue?"):
                    try:
                        from database.office_operation import rotate_all_office_codes_weekly
                        count = rotate_all_office_codes_weekly()
                        messagebox.showinfo("Weekly Rotation Complete", 
                                           f"Successfully rotated codes for {count} offices!\n" +
                                           "All codes have been synced to Firebase.")
                        refresh_office_list()
                    except Exception as e:
                        messagebox.showerror("Error", f"Weekly rotation failed: {str(e)}")
            
            def daily_rotation():
                """Daily code rotation"""
                if messagebox.askyesno("Daily Code Rotation", 
                                      "Rotate ALL office codes?\n\n" +
                                      "This will:\n" +
                                      "• Generate new 4-digit codes for all offices\n" +
                                      "• Sync codes to Firebase automatically\n" +
                                      "• Old codes will become invalid\n\n" +
                                      "Continue?"):
                    try:
                        from database.office_operation import rotate_all_office_codes_daily
                        count = rotate_all_office_codes_daily()
                        messagebox.showinfo("Daily Rotation Complete", 
                                           f"Successfully rotated codes for {count} offices!\n" +
                                           "All codes have been synced to Firebase.")
                        refresh_office_list()
                    except Exception as e:
                        messagebox.showerror("Error", f"Daily rotation failed: {str(e)}")
            
            def sync_firebase():
                """Sync all offices to Firebase"""
                if messagebox.askyesno("Sync to Firebase", 
                                      "Sync all current office codes to Firebase?\n\n" +
                                      "This will upload all current codes to the online database."):
                    try:
                        from database.office_operation import sync_all_offices_to_firebase
                        if sync_all_offices_to_firebase():
                            messagebox.showinfo("Sync Complete", "All office codes synced to Firebase!")
                        else:
                            messagebox.showerror("Sync Failed", "Failed to sync codes to Firebase!")
                    except Exception as e:
                        messagebox.showerror("Error", f"Firebase sync error: {str(e)}")
            
            # Rotation buttons
            tk.Button(rotation_btn_frame, text="📅 Weekly Rotation", font=("Arial", button_font_size),
                     bg="#3498DB", fg="white", cursor="hand2", width=18,
                     command=weekly_rotation).pack(side="left", padx=(0, 5))
            
            tk.Button(rotation_btn_frame, text="🗓️ Daily Rotation", font=("Arial", button_font_size),
                     bg="#E67E22", fg="white", cursor="hand2", width=18,
                     command=daily_rotation).pack(side="left", padx=5)
            
            tk.Button(rotation_btn_frame, text="🔥 Sync Firebase", font=("Arial", button_font_size),
                     bg="#27AE60", fg="white", cursor="hand2", width=18,
                     command=sync_firebase).pack(side="right", padx=(5, 0))
            
            # Load initial data
            refresh_office_list()
            
    # Helper functions
    def run_function(self, function_name):
        """Run admin function and show result"""
        try:
            result = self.admin_functions[function_name]()
            
            # Success messages with icons
            messages = {
                'enroll': ("✅ Success", "Enrollment completed successfully!\nCheck terminal for details."),
                'sync': ("🔄 Sync Complete", "Database synchronized successfully!\nCheck terminal for details."),
                'clear_records': ("🧹 Records Cleared", "All time records have been cleared successfully.")
            }
            
            if function_name in messages:
                title, msg = messages[function_name]
                self.root.after(0, lambda: messagebox.showinfo(title, msg, icon='info'))
                
        except Exception as e:
            error_message = str(e)
            self.root.after(0, lambda: messagebox.showerror("❌ Error", f"Operation failed:\n\n{str(error_message)}"))
    
    def close(self):
        """Close the GUI"""
        try:
            self.root.quit()
            self.root.destroy()
        except:
            pass
    
    def run(self):
        """Run the GUI"""
        try:
            # Bind escape key
            self.root.bind('<Escape>', lambda e: self.close())
            
            # Start main loop
            self.root.mainloop()
        except Exception as e:
            print(f"Error running GUI: {e}")
            self.close()
            
    def setup_window(self):
        """Setup the main window with enhanced styling - RESPONSIVE FULLSCREEN"""
        self.root.title("MotorPass - Admin Control Center")
        self.root.configure(bg=self.colors['light'])
        
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
        
        # Bind Escape key to toggle fullscreen (for admin access)
        self.root.bind('<F11>', self.toggle_fullscreen)
        
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
        
    def create_variables(self):
        """Create all tkinter variables"""
        self.time_string = tk.StringVar()
        self.date_string = tk.StringVar()
        self.status_text = tk.StringVar(value="🔐 Admin authentication required")
        self.update_time()
        
    def update_time(self):
        """Update time display"""
        try:
            if not hasattr(self, 'root') or not self.root.winfo_exists():
                return
                
            now = datetime.now()
            self.time_string.set(now.strftime("%I:%M:%S %p"))
            self.date_string.set(now.strftime("%A, %B %d, %Y"))
            
            if self.root.winfo_exists():
                self.root.after(1000, self.update_time)
        except:
            pass
    
    def create_authentication_screen(self):
        """Create the authentication screen - RESPONSIVE"""
        # Clear window
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Main container with gradient background
        main_container = tk.Frame(self.root, bg=self.colors['primary'])
        main_container.pack(fill="both", expand=True)
        
        # Create gradient effect
        gradient_frame = tk.Canvas(main_container, highlightthickness=0)
        gradient_frame.pack(fill="both", expand=True)
        
        # Responsive card sizing
        if self.is_square_display:
            card_width = int(self.display_size * 0.5)
            card_height = int(self.display_size * 0.55)
        else:
            card_width = int(self.display_size * 0.45)
            card_height = int(self.display_size * 0.5)
            
        # Authentication card
        auth_card = tk.Frame(gradient_frame, bg=self.colors['white'], relief='flat')
        auth_card.place(relx=0.5, rely=0.5, anchor='center', width=card_width, height=card_height)
        
        # Card shadow effect
        shadow = tk.Frame(gradient_frame, bg='#D0D0D0')
        shadow.place(relx=0.5, rely=0.5, anchor='center', width=card_width+10, height=card_height+10)
        auth_card.lift()
        
        # Responsive logo section
        logo_height = max(100, int(card_height * 0.25))
        logo_frame = tk.Frame(auth_card, bg=self.colors['primary'], height=logo_height)
        logo_frame.pack(fill="x")
        logo_frame.pack_propagate(False)
        
        # Logo with responsive size
        logo_size = max(60, int(logo_height * 0.6))
        logo_container = tk.Frame(logo_frame, bg=self.colors['gold'], width=logo_size, height=logo_size)
        logo_container.place(relx=0.5, rely=0.5, anchor='center')
        
        logo_icon_size = max(24, int(logo_size * 0.4))
        tk.Label(logo_container, text="🛡️", font=("Arial", logo_icon_size), 
                bg=self.colors['gold'], fg=self.colors['primary']).place(relx=0.5, rely=0.5, anchor='center')
        
        # Responsive fonts
        title_font_size = max(18, int(self.display_size / 45))
        subtitle_font_size = max(11, int(self.display_size / 70))
        status_font_size = max(10, int(self.display_size / 80))
        button_font_size = max(12, int(self.display_size / 65))
        
        # Title
        title_padding = max(20, int(card_height * 0.05))
        tk.Label(auth_card, text="ADMIN ACCESS CONTROL", 
                font=("Arial", title_font_size, "bold"), fg=self.colors['primary'], bg=self.colors['white']).pack(pady=(title_padding, 8))
        
        # Subtitle
        tk.Label(auth_card, text="Fingerprint Authentication Required", 
                font=("Arial", subtitle_font_size), fg=self.colors['secondary'], bg=self.colors['white']).pack(pady=(0, title_padding))
        
        # Status with animated dots
        status_frame = tk.Frame(auth_card, bg=self.colors['white'])
        status_frame.pack(pady=15)
        
        self.status_label = tk.Label(status_frame, textvariable=self.status_text, 
                                    font=("Arial", status_font_size), fg=self.colors['info'], bg=self.colors['white'])
        self.status_label.pack()
        
        # Authentication button with hover effect - responsive sizing
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
        
        # Add hover effects
        self.auth_button.bind("<Enter>", lambda e: self.auth_button.config(bg=self.colors['info']))
        self.auth_button.bind("<Leave>", lambda e: self.auth_button.config(bg=self.colors['success']))
        
        # Exit button - responsive
        exit_font_size = max(9, int(self.display_size / 90))
        exit_padding = max(15, int(card_width * 0.06))
        
        exit_btn = tk.Button(auth_card, text="EXIT", 
                            font=("Arial", exit_font_size), bg=self.colors['secondary'], fg=self.colors['white'],
                            activebackground=self.colors['accent'],
                            padx=exit_padding, pady=6, cursor="hand2", relief='flat', bd=0,
                            command=self.close)
        exit_btn.pack(pady=(0, 15))
    
    def start_authentication(self):
        """Start fingerprint authentication"""
        self.status_text.set("🔄 Authenticating... Place finger on sensor")
        self.auth_button.config(state='disabled', text="⏳ AUTHENTICATING...")
        
        # Run authentication in thread
        thread = threading.Thread(target=self.run_authentication, daemon=True)
        thread.start()
    
    def run_authentication(self):
        """Run authentication process"""
        try:
            # Call the authentication function
            if self.admin_functions['authenticate']():
                self.authenticated = True
                self.root.after(0, self.show_admin_panel)
            else:
                self.root.after(0, lambda: self.status_text.set("❌ Authentication failed! Access denied."))
                self.root.after(0, lambda: self.auth_button.config(state='normal', text="🔓 START AUTHENTICATION"))
                self.root.after(2000, lambda: self.status_text.set("🔐 Admin authentication required"))
        except Exception as e:
            self.root.after(0, lambda: self.status_text.set(f"❌ Error: {str(e)}"))
            self.root.after(0, lambda: self.auth_button.config(state='normal', text="🔓 START AUTHENTICATION"))
    
    def show_admin_panel(self):
        """Show the enhanced main admin panel - RESPONSIVE"""
        # Clear window
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Main container
        main_container = tk.Frame(self.root, bg=self.colors['light'])
        main_container.pack(fill="both", expand=True)
        
        # Enhanced header
        self.create_enhanced_header(main_container)
        
        # Content area - responsive layout
        content_container = tk.Frame(main_container, bg=self.colors['light'])
        content_container.pack(fill="both", expand=True)
        
        if self.is_square_display:
            # For square displays, stack vertically for better space utilization
            # Stats at top, main content below
            self.create_stats_top_bar(content_container)
            
            # Main content area
            main_content = tk.Frame(content_container, bg=self.colors['white'])
            main_content.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        else:
            # For wider displays, use sidebar layout
            # Stats sidebar
            self.create_stats_sidebar(content_container)
            
            # Main content area
            main_content = tk.Frame(content_container, bg=self.colors['white'])
            main_content.pack(side="right", fill="both", expand=True, padx=(0, 15), pady=15)
        
        # Menu cards
        self.create_menu_cards(main_content)
        
        # Footer
        self.create_enhanced_footer(main_container)
    
    def create_enhanced_header(self, parent):
        """Create enhanced header with modern design - RESPONSIVE"""
        # Responsive header height
        header_height = max(60, int(self.screen_height * 0.08))
        header = tk.Frame(parent, bg=self.colors['primary'], height=header_height)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        # Add subtle shadow
        shadow = tk.Frame(parent, bg='#E0E0E0', height=2)
        shadow.pack(fill="x")
        
        # Header content with responsive padding
        header_padding = max(15, int(self.screen_width * 0.02))
        header_content = tk.Frame(header, bg=self.colors['primary'])
        header_content.pack(fill="both", expand=True, padx=header_padding)
        
        # Logo and title section
        left_section = tk.Frame(header_content, bg=self.colors['primary'])
        left_section.pack(side="left", fill="y")
        
        # Modern logo with responsive sizing
        logo_size = max(40, int(header_height * 0.6))
        logo_bg = tk.Frame(left_section, bg=self.colors['gold'], width=logo_size, height=logo_size)
        logo_bg.pack(side="left", pady=(header_height - logo_size) // 2)
        logo_bg.pack_propagate(False)
        
        logo_icon_size = max(16, int(logo_size * 0.4))
        tk.Label(logo_bg, text="⚡", font=("Arial", logo_icon_size), 
                bg=self.colors['gold'], fg=self.colors['primary']).place(relx=0.5, rely=0.5, anchor="center")
        
        # Title with responsive fonts
        title_section = tk.Frame(left_section, bg=self.colors['primary'])
        title_section.pack(side="left", padx=(15, 0), fill="y")
        
        title_font_size = max(16, int(self.display_size / 50))
        subtitle_font_size = max(8, int(self.display_size / 100))
        
        title_y_padding = (header_height - 40) // 2
        tk.Label(title_section, text="ADMIN CONTROL CENTER", 
                font=("Arial", title_font_size, "bold"), fg=self.colors['white'], bg=self.colors['primary']).pack(anchor="w", pady=(title_y_padding, 0))
        tk.Label(title_section, text="MotorPass Management System",
                font=("Arial", subtitle_font_size), fg=self.colors['light'], bg=self.colors['primary']).pack(anchor="w")
        
        # Right section with clock - responsive
        right_section = tk.Frame(header_content, bg=self.colors['primary'])
        right_section.pack(side="right", fill="y")
        
        # Modern clock display with responsive sizing
        clock_width = max(140, int(self.screen_width * 0.12))
        clock_height = max(50, int(header_height * 0.7))
        clock_container = tk.Frame(right_section, bg=self.colors['secondary'], relief='flat',
                                  width=clock_width, height=clock_height)
        clock_container.pack(pady=(header_height - clock_height) // 2, padx=8)
        clock_container.pack_propagate(False)
        
        time_frame = tk.Frame(clock_container, bg=self.colors['secondary'])
        time_frame.pack(expand=True)
        
        time_font_size = max(12, int(self.display_size / 65))
        date_font_size = max(7, int(self.display_size / 120))
        
        tk.Label(time_frame, textvariable=self.time_string, font=("Arial", time_font_size, "bold"), 
                fg=self.colors['gold'], bg=self.colors['secondary']).pack(pady=(8, 0))
        tk.Label(time_frame, textvariable=self.date_string, font=("Arial", date_font_size), 
                fg=self.colors['light'], bg=self.colors['secondary']).pack()
    
    def create_stats_sidebar(self, parent):
        """Create statistics sidebar for wide displays"""
        # Responsive sidebar width
        sidebar_width = max(200, int(self.screen_width * 0.20))
        sidebar = tk.Frame(parent, bg=self.colors['secondary'], width=sidebar_width)
        sidebar.pack(side="left", fill="y", padx=(15, 15), pady=15)
        sidebar.pack_propagate(False)
        
        # Responsive title
        title_font_size = max(12, int(self.display_size / 65))
        tk.Label(sidebar, text="📊 LIVE STATISTICS", 
                font=("Arial", title_font_size, "bold"), fg=self.colors['white'], 
                bg=self.colors['secondary']).pack(pady=15)
        
        # Load stats
        try:
            stats = self.admin_functions['get_stats']()
        except:
            stats = {}
        
        # Stat cards with responsive spacing
        card_spacing = max(8, int(self.screen_height / 80))
        
        self.create_stat_card(sidebar, "👥", "Total Users", 
                            stats.get('total_students', 0) + stats.get('total_staff', 0), 
                            self.colors['info'], card_spacing)
        
        self.create_stat_card(sidebar, "🎓", "Students", 
                            stats.get('total_students', 0), 
                            self.colors['success'], card_spacing)
        
        self.create_stat_card(sidebar, "👔", "Staff", 
                            stats.get('total_staff', 0), 
                            self.colors['warning'], card_spacing)
        
        self.create_stat_card(sidebar, "", "Currently Inside", 
                            stats.get('users_currently_in', 0), 
                            self.colors['accent'], card_spacing)
        
        # Activity indicator
        activity_frame = tk.Frame(sidebar, bg=self.colors['primary'])
        activity_frame.pack(fill="x", padx=15, pady=15)
        
        activity_title_size = max(9, int(self.display_size / 90))
        activity_value_size = max(14, int(self.display_size / 55))
        
        tk.Label(activity_frame, text="📈 Today's Activity", 
                font=("Arial", activity_title_size, "bold"), fg=self.colors['white'], 
                bg=self.colors['primary']).pack(pady=8)
        
        tk.Label(activity_frame, text=f"{stats.get('todays_activity', 0)} Actions", 
                font=("Arial", activity_value_size, "bold"), fg=self.colors['gold'], 
                bg=self.colors['primary']).pack(pady=(0, 8))
    
    def create_stats_top_bar(self, parent):
        """Create statistics top bar for square displays"""
        # Responsive top bar height
        topbar_height = max(80, int(self.screen_height * 0.12))
        topbar = tk.Frame(parent, bg=self.colors['secondary'], height=topbar_height)
        topbar.pack(fill="x", padx=15, pady=(15, 0))
        topbar.pack_propagate(False)
        
        # Content container
        topbar_content = tk.Frame(topbar, bg=self.colors['secondary'])
        topbar_content.pack(expand=True, pady=8)
        
        # Title
        title_font_size = max(11, int(self.display_size / 75))
        tk.Label(topbar_content, text="📊 LIVE STATISTICS", 
                font=("Arial", title_font_size, "bold"), fg=self.colors['white'], 
                bg=self.colors['secondary']).pack()
        
        # Load stats
        try:
            stats = self.admin_functions['get_stats']()
        except:
            stats = {}
        
        # Stats container - horizontal layout
        stats_container = tk.Frame(topbar_content, bg=self.colors['secondary'])
        stats_container.pack(expand=True, pady=(5, 0))
        
        # Responsive stat items
        stat_font_size = max(8, int(self.display_size / 110))
        stat_value_size = max(12, int(self.display_size / 70))
        
        stats_data = [
            ("👥", "Total", stats.get('total_students', 0) + stats.get('total_staff', 0), self.colors['info']),
            ("🎓", "Students", stats.get('total_students', 0), self.colors['success']),
            ("👔", "Staff", stats.get('total_staff', 0), self.colors['warning']),
            ("", "Inside", stats.get('users_currently_in', 0), self.colors['accent']),
            ("📈", "Activity", stats.get('todays_activity', 0), self.colors['gold'])
        ]
        
        for icon, label, value, color in stats_data:
            stat_item = tk.Frame(stats_container, bg=self.colors['secondary'])
            stat_item.pack(side="left", padx=12)
            tk.Label(stat_item, text=f"{icon} {label}", font=("Arial", stat_font_size), 
                    fg=self.colors['light'], bg=self.colors['secondary']).pack()
            tk.Label(stat_item, text=str(value), font=("Arial", stat_value_size, "bold"), 
                    fg=color, bg=self.colors['secondary']).pack()
    
    def create_stat_card(self, parent, icon, label, value, color, spacing=10):
        """Create a statistics card - RESPONSIVE"""
        card = tk.Frame(parent, bg=self.colors['dark'])
        card.pack(fill="x", padx=12, pady=spacing)
        
        # Content frame with responsive padding
        content_padding = max(8, int(self.display_size / 100))
        content = tk.Frame(card, bg=self.colors['dark'])
        content.pack(fill="x", padx=content_padding, pady=content_padding)
        
        # Icon and label with responsive fonts
        top_row = tk.Frame(content, bg=self.colors['dark'])
        top_row.pack(fill="x")
        
        stat_label_size = max(9, int(self.display_size / 90))
        stat_value_size = max(16, int(self.display_size / 50))
        
        tk.Label(top_row, text=f"{icon} {label}", 
                font=("Arial", stat_label_size), fg=self.colors['light'], 
                bg=self.colors['dark']).pack(side="left")
        
        # Value
        tk.Label(content, text=str(value), 
                font=("Arial", stat_value_size, "bold"), fg=color, 
                bg=self.colors['dark']).pack(anchor="w", pady=(3, 0))
    
    def create_menu_cards(self, parent):
        """Create enhanced menu cards with access control - RESPONSIVE"""
        # Title with responsive font
        title_font_size = max(16, int(self.display_size / 50))
        title_text = "SYSTEM FUNCTIONS"
        if self.user_role == "guard":
            title_text += " (Guard Access)"
        elif self.user_role == "super_admin":
            title_text += " (Super Admin Access)"
            
        title_padding = max(15, int(self.screen_height * 0.02))
        tk.Label(parent, text=title_text, 
                font=("Arial", title_font_size, "bold"), fg=self.colors['primary'], 
                bg=self.colors['white']).pack(pady=(title_padding, title_padding))
        
        # Cards container with responsive padding
        cards_padding = max(20, int(self.screen_width * 0.03))
        cards_container = tk.Frame(parent, bg=self.colors['white'])
        cards_container.pack(fill="both", expand=True, padx=cards_padding)
        
        # Responsive card layout
        if self.is_square_display:
            # For square displays, use 2x4 grid (2 columns, 4 rows)
            rows = [tk.Frame(cards_container, bg=self.colors['white']) for _ in range(4)]
            for i, row in enumerate(rows):
                row.pack(fill="x", pady=(0, 12))
            
            # Cards data
            cards_data = [
                ("👤", "Register New User", "Register student/staff with fingerprint", self.enroll_user, self.colors['success'], "enroll"),
                ("👥", "View Users", "Display all registered users", self.view_users, self.colors['info'], "view_users"),
                ("🗑️", "Update User", "Remove user fingerprint", self.delete_user, self.colors['accent'], "delete_fingerprint"),
                ("🔄", "Sync Database", "Import from Google Sheets", self.sync_database, self.colors['warning'], "sync"),
                ("🕒", "Time Records", "View attendance history", self.view_time_records, self.colors['secondary'], "get_time_records"),
                ("🧹", "Clear Records", "Delete time records", self.clear_time_records, self.colors['dark'], "clear_records"),
                ("🏢", "System Maintenance", "Manage visitor offices & security codes", self.show_office_management, self.colors['gold'], "system_maintenance")
            ]
            
            # Arrange cards in 2x4 grid
            for i, card_data in enumerate(cards_data):
                row_index = i // 2
                if row_index < len(rows):
                    self.create_function_card(rows[row_index], *card_data)
                    
        else:
            # For wider displays, use 3 rows
            row1 = tk.Frame(cards_container, bg=self.colors['white'])
            row1.pack(fill="x", pady=(0, 15))
            
            row2 = tk.Frame(cards_container, bg=self.colors['white'])
            row2.pack(fill="x", pady=(0, 15))
            
            row3 = tk.Frame(cards_container, bg=self.colors['white'])
            row3.pack(fill="x")
            
            # Row 1 cards
            self.create_function_card(row1, "👤", "Enroll New User", 
                                     "Register student/staff with fingerprint",
                                     self.enroll_user, self.colors['success'], "enroll")
            
            self.create_function_card(row1, "👥", "View Users", 
                                     "Display all registered users",
                                     self.view_users, self.colors['info'], "view_users")
            
            self.create_function_card(row1, "🗑️", "Delete User", 
                                     "Remove user fingerprint",
                                     self.delete_user, self.colors['accent'], "delete_fingerprint")
            
            # Row 2 cards
            self.create_function_card(row2, "🔄", "Sync Database", 
                                     "Import from Google Sheets",
                                     self.sync_database, self.colors['warning'], "sync")
            
            self.create_function_card(row2, "🕒", "Time Records", 
                                     "View attendance history",
                                     self.view_time_records, self.colors['secondary'], "get_time_records")
            
            self.create_function_card(row2, "🧹", "Clear Records", 
                                     "Delete time records",
                                     self.clear_time_records, self.colors['dark'], "clear_records")
            
            # Row 3 - System Maintenance
            self.create_function_card(row3, "🏢", "System Maintenance", 
                                     "Manage visitor offices & security codes",
                                     self.show_office_management, self.colors['gold'], "system_maintenance")

    def create_function_card(self, parent, icon, title, description, command, color, function_name=None):
        """Create an enhanced function card with access control - RESPONSIVE"""
        # Check access
        has_access = True
        if function_name:
            has_access = self.has_access(function_name)
        
        # Adjust colors for restricted access
        if not has_access:
            color = '#CCCCCC'
            
        # Card frame with shadow - responsive spacing
        card_spacing = max(6, int(self.screen_width * 0.008))
        card_container = tk.Frame(parent, bg=self.colors['white'])
        card_container.pack(side="left", fill="both", expand=True, padx=card_spacing)
        
        # Shadow effect
        shadow = tk.Frame(card_container, bg='#D5D5D5')
        shadow.place(x=2, y=2, relwidth=1, relheight=1)
        
        # Main card
        card = tk.Frame(card_container, bg=self.colors['light'], relief='flat', bd=0)
        card.pack(fill="both", expand=True)
        
        # Content with responsive padding
        content_padding = max(12, int(self.display_size / 70))
        content = tk.Frame(card, bg=self.colors['light'])
        content.pack(fill="both", expand=True, padx=content_padding, pady=content_padding)
        
        # Icon circle with responsive sizing
        icon_size = max(45, int(self.display_size / 18))
        icon_frame = tk.Frame(content, bg=self.colors['white'], width=icon_size, height=icon_size)
        icon_frame.pack(pady=(0, 10))
        icon_frame.pack_propagate(False)
        
        icon_font_size = max(18, int(icon_size * 0.4))
        icon_label = tk.Label(icon_frame, text=icon, font=("Arial", icon_font_size), 
                             bg=self.colors['white'], fg=color)
        icon_label.place(relx=0.5, rely=0.5, anchor='center')
        
        # Title with responsive font - grey out if no access
        title_font_size = max(11, int(self.display_size / 75))
        title_color = self.colors['dark'] if has_access else '#999999'
        title_label = tk.Label(content, text=title, font=("Arial", title_font_size, "bold"), 
                              fg=title_color, bg=self.colors['light'])
        title_label.pack(pady=(0, 4))
        
        # Description with responsive font - grey out if no access
        desc_font_size = max(8, int(self.display_size / 100))
        desc_color = self.colors['secondary'] if has_access else '#BBBBBB'
        if not has_access:
            description_text = description + " (Access Restricted)"
        else:
            description_text = description
            
        desc_wrap_length = max(120, int(self.display_size / 7))
        desc_label = tk.Label(content, text=description_text, font=("Arial", desc_font_size), 
                             fg=desc_color, bg=self.colors['light'], wraplength=desc_wrap_length)
        desc_label.pack()
        
        # Make card clickable based on access
        clickable_widgets = [card, content, icon_frame, icon_label, title_label, desc_label]
        
        if has_access:
            # Enable access - normal click behavior
            for widget in clickable_widgets:
                widget.bind("<Button-1>", lambda e: command())
                widget.config(cursor="hand2")
        else:
            # Restrict access - show access denied message
            def show_access_denied(event=None):
                messagebox.showwarning("Access Denied", 
                                     f"Your role ({self.user_role}) does not have access to this function.\n\n" +
                                     "Only Super Admin can access this feature.")
            
            for widget in clickable_widgets:
                widget.bind("<Button-1>", show_access_denied)
                widget.config(cursor="X_cursor")
                    
    def create_enhanced_footer(self, parent):
        """Create enhanced footer - RESPONSIVE"""
        # Responsive footer height
        footer_height = max(50, int(self.screen_height * 0.08))
        footer = tk.Frame(parent, bg=self.colors['dark'], height=footer_height)
        footer.pack(fill="x")
        footer.pack_propagate(False)
        
        footer_content = tk.Frame(footer, bg=self.colors['dark'])
        footer_content.pack(expand=True)
        
        # Buttons with modern style and responsive sizing
        buttons_frame = tk.Frame(footer_content, bg=self.colors['dark'])
        buttons_frame.pack(pady=(footer_height - 35) // 2)
        
        # Responsive button sizing
        button_font_size = max(10, int(self.display_size / 80))
        button_padding_x = max(20, int(self.display_size / 40))
        button_padding_y = max(8, int(self.display_size / 100))
        
        # Dashboard button (only for super admin)
        if self.user_role == "super_admin":
            dash_btn = tk.Button(buttons_frame, text="📊 WEB DASHBOARD", 
                                font=("Arial", button_font_size, "bold"), 
                                bg=self.colors['gold'], fg=self.colors['dark'],
                                activebackground=self.colors['warning'],
                                padx=button_padding_x, pady=button_padding_y, cursor="hand2", relief='flat', bd=0,
                                command=self.open_dashboard)
            dash_btn.pack(side="left", padx=8)
            
            # Add hover effects
            dash_btn.bind("<Enter>", lambda e: dash_btn.config(bg=self.colors['warning']))
            dash_btn.bind("<Leave>", lambda e: dash_btn.config(bg=self.colors['gold']))
        
        # Exit button (always show for everyone)
        exit_btn = tk.Button(buttons_frame, text="🚪 EXIT ADMIN PANEL", 
                            font=("Arial", button_font_size, "bold"), 
                            bg=self.colors['accent'], fg=self.colors['white'],
                            activebackground='#C0392B',
                            padx=button_padding_x, pady=button_padding_y, cursor="hand2", relief='flat', bd=0,
                            command=self.exit_system)
        exit_btn.pack(side="left", padx=8)
        
        # Add hover effects for exit button
        exit_btn.bind("<Enter>", lambda e: exit_btn.config(bg='#C0392B'))
        exit_btn.bind("<Leave>", lambda e: exit_btn.config(bg=self.colors['accent']))

