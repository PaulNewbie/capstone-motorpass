# ui/components/ui_components.py - Reusable UI Components
# FIXED: Complete implementation matching legacy admin_gui.py

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os

class UIComponents:
    """Reusable UI components library - FIXED from legacy admin_gui.py"""
    
    @staticmethod
    def create_scrollable_container(parent, colors):
        """Create a scrollable container - from legacy admin_gui.py"""
        # Create canvas and scrollbar
        canvas = tk.Canvas(parent, bg=colors['white'])
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=colors['white'])
        
        # Configure scrolling
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack scrollable components
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        return scrollable_frame
    
    @staticmethod
    def create_menu_card_layout(parent, cards_data, colors, screen_width, screen_height, 
                               display_size, is_square_display, has_access_func=None):
        """Create menu card layout - EXACT from legacy admin_gui.py"""
        
        # Title with responsive font - EXACT from legacy
        title_font_size = max(16, int(display_size / 50))
        title_text = "SYSTEM FUNCTIONS"
        
        title_padding = max(15, int(screen_height * 0.02))
        tk.Label(parent, text=title_text,
                font=("Arial", title_font_size, "bold"), fg=colors['primary'],
                bg=colors['white']).pack(pady=(title_padding, title_padding))
        
        # Cards container with responsive padding - EXACT from legacy
        cards_padding = max(20, int(screen_width * 0.03))
        cards_container = tk.Frame(parent, bg=colors['white'])
        cards_container.pack(fill="both", expand=True, padx=cards_padding)
        
        # Responsive card layout - EXACT from legacy admin_gui.py logic
        if is_square_display:
            # For square displays (1024x768), use 2x4 grid - EXACT from legacy
            rows = [tk.Frame(cards_container, bg=colors['white']) for _ in range(4)]
            for i, row in enumerate(rows):
                row.pack(fill="x", pady=(0, max(8, int(screen_height * 0.01))))
            
            # 2x4 distribution - EXACT from legacy
            row_assignments = [0, 0, 1, 1, 1, 2, 2]  # 2-3-2 distribution
        else:
            # For wider displays, use 3 rows - EXACT from legacy
            row1 = tk.Frame(cards_container, bg=colors['white'])
            row1.pack(fill="x", pady=(0, max(10, int(screen_height * 0.015))))
            
            row2 = tk.Frame(cards_container, bg=colors['white'])
            row2.pack(fill="x", pady=(0, max(10, int(screen_height * 0.015))))
            
            row3 = tk.Frame(cards_container, bg=colors['white'])
            row3.pack(fill="x")
            
            rows = [row1, row2, row3]
            row_assignments = [0, 0, 0, 1, 1, 1, 2]  # 3-3-1 distribution
        
        # Create cards - EXACT from legacy
        for i, card_data in enumerate(cards_data):
            if i < len(row_assignments):
                row_index = row_assignments[i]
                if row_index < len(rows):
                    icon, title, description, command, color, function_name = card_data
                    
                    # Check access if function provided
                    has_access = True
                    if has_access_func and function_name:
                        has_access = has_access_func(function_name)
                    
                    UIComponents.create_function_card(
                        rows[row_index], icon, title, description, command, color, 
                        function_name, has_access, colors, display_size, screen_width
                    )
    
    @staticmethod
    def create_function_card(parent, icon, title, description, command, color, 
                           function_name, has_access, colors, display_size, screen_width):
        """Create an enhanced function card - EXACT from legacy admin_gui.py"""
        
        # Adjust colors for restricted access - EXACT from legacy
        if not has_access:
            color = '#CCCCCC'
        
        # Card frame with shadow - responsive spacing - EXACT from legacy
        card_spacing = max(6, int(screen_width * 0.008))
        card_container = tk.Frame(parent, bg=colors['white'])
        card_container.pack(side="left", fill="both", expand=True, padx=card_spacing)
        
        # Shadow effect - EXACT from legacy
        shadow = tk.Frame(card_container, bg='#D5D5D5')
        shadow.place(x=2, y=2, relwidth=1, relheight=1)
        
        # Main card - EXACT from legacy
        card = tk.Frame(card_container, bg=colors['light'], relief='flat', bd=0)
        card.pack(fill="both", expand=True)
        
        # Content with responsive padding - EXACT from legacy
        content_padding = max(12, int(display_size / 70))
        content = tk.Frame(card, bg=colors['light'])
        content.pack(fill="both", expand=True, padx=content_padding, pady=content_padding)
        
        # Icon circle with responsive sizing - EXACT from legacy
        icon_size = max(45, int(display_size / 18))
        icon_frame = tk.Frame(content, bg=colors['white'], width=icon_size, height=icon_size)
        icon_frame.pack(pady=(0, 10))
        icon_frame.pack_propagate(False)
        
        icon_font_size = max(18, int(icon_size * 0.4))
        icon_label = tk.Label(icon_frame, text=icon, font=("Arial", icon_font_size), 
                             bg=colors['white'], fg=color)
        icon_label.place(relx=0.5, rely=0.5, anchor='center')
        
        # Title with responsive font - EXACT from legacy
        title_font_size = max(11, int(display_size / 75))
        title_color = colors['dark'] if has_access else '#999999'
        title_label = tk.Label(content, text=title, font=("Arial", title_font_size, "bold"), 
                              fg=title_color, bg=colors['light'])
        title_label.pack(pady=(0, 4))
        
        # Description with responsive font - EXACT from legacy
        desc_font_size = max(8, int(display_size / 100))
        desc_color = colors['secondary'] if has_access else '#BBBBBB'
        if not has_access:
            description_text = description + " (Access Restricted)"
        else:
            description_text = description
            
        desc_wrap_length = max(120, int(display_size / 7))
        desc_label = tk.Label(content, text=description_text, font=("Arial", desc_font_size), 
                             fg=desc_color, bg=colors['light'], wraplength=desc_wrap_length)
        desc_label.pack()
        
        # Make card clickable based on access - EXACT from legacy
        clickable_widgets = [card, content, icon_frame, icon_label, title_label, desc_label]
        
        if has_access:
            # Enable access - normal click behavior - EXACT from legacy
            for widget in clickable_widgets:
                widget.bind("<Button-1>", lambda e: command())
                widget.config(cursor="hand2")
        else:
            # Restrict access - show access denied message - EXACT from legacy
            def show_access_denied(event=None):
                import tkinter.messagebox
                tkinter.messagebox.showwarning("Access Denied", 
                                     "Your role does not have access to this function.\n\n" +
                                     "Only Super Admin can access this feature.")
            
            for widget in clickable_widgets:
                widget.bind("<Button-1>", show_access_denied)
                widget.config(cursor="X_cursor")
    
    @staticmethod
    def darken_color(hex_color, factor=0.8):
        """Darken a hex color for hover effects"""
        try:
            hex_color = hex_color.lstrip('#')
            rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            darkened = tuple(int(c * factor) for c in rgb)
            return '#{:02x}{:02x}{:02x}'.format(*darkened)
        except:
            return hex_color
    
    @staticmethod
    def create_office_management_section(parent, colors, font_sizes, refresh_callback=None):
        """Create complete office management section - FIXED from legacy admin_gui.py"""
        try:
            from database.office_operation import get_all_offices, add_office, update_office_code, delete_office
        except ImportError:
            # Show error if office operations not available
            error_label = tk.Label(parent, text="⚠️ Office Management System Not Available",
                                 font=("Arial", font_sizes['button'], "bold"),
                                 fg=colors['accent'], bg=colors['white'])
            error_label.pack(pady=20)
            return None
        
        # Office list section
        tk.Label(parent, text="📋 Current Offices:",
                font=("Arial", font_sizes['button'], "bold"),
                fg=colors['dark'], bg=colors['white']).pack(anchor="w", pady=(0, 10))
        
        # Office listbox with scrollbar
        listbox_frame = tk.Frame(parent, bg=colors['white'])
        listbox_frame.pack(fill="x", pady=(0, 10))
        
        offices_listbox = tk.Listbox(listbox_frame, height=6,
                                    font=("Arial", font_sizes['card_description']))
        scrollbar = tk.Scrollbar(listbox_frame, orient="vertical")
        offices_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=offices_listbox.yview)
        
        offices_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        def refresh_office_list():
            """Refresh the office list display"""
            offices_listbox.delete(0, tk.END)
            offices = get_all_offices()
            for office in offices:
                offices_listbox.insert(tk.END, f"{office['office_name']} (Code: {office['office_code']})")
        
        def add_new_office():
            """Add new office with dialog"""
            office_name = tk.simpledialog.askstring("Add Office", "Enter office name:")
            if office_name and office_name.strip():
                if add_office(office_name.strip()):
                    tk.messagebox.showinfo("Success", f"Office '{office_name}' added successfully!")
                    refresh_office_list()
                else:
                    tk.messagebox.showerror("Error", "Failed to add office!")
        
        def update_office_code_gui():
            """Update office security code"""
            selection = offices_listbox.curselection()
            if not selection:
                tk.messagebox.showwarning("Warning", "Please select an office first!")
                return
            
            selected_text = offices_listbox.get(selection[0])
            office_name = selected_text.split(" (Code:")[0]
            
            new_code = tk.simpledialog.askstring("Update Code", 
                                               f"Enter new 4-digit code for '{office_name}':",
                                               initialvalue="")
            if new_code and len(new_code) == 4 and new_code.isdigit():
                if update_office_code(office_name, new_code):
                    tk.messagebox.showinfo("Success", f"Office code updated successfully!")
                    refresh_office_list()
                else:
                    tk.messagebox.showerror("Error", "Failed to update office code!")
            elif new_code:
                tk.messagebox.showerror("Error", "Code must be exactly 4 digits!")
        
        def delete_office_gui():
            """Delete selected office"""
            selection = offices_listbox.curselection()
            if not selection:
                tk.messagebox.showwarning("Warning", "Please select an office first!")
                return
            
            selected_text = offices_listbox.get(selection[0])
            office_name = selected_text.split(" (Code:")[0]
            
            confirm = tk.messagebox.askyesno("Confirm Delete", 
                                           f"Are you sure you want to delete '{office_name}'?")
            if confirm:
                if delete_office(office_name):
                    tk.messagebox.showinfo("Success", "Office deleted successfully!")
                    refresh_office_list()
                else:
                    tk.messagebox.showerror("Error", "Failed to delete office!")
        
        # Control buttons
        button_frame = tk.Frame(parent, bg=colors['white'])
        button_frame.pack(fill="x", pady=(10, 0))
        
        tk.Button(button_frame, text="➕ Add Office", command=add_new_office,
                 bg=colors['success'], fg="white", font=("Arial", font_sizes['card_description'], "bold"),
                 cursor="hand2", padx=10, pady=5).pack(side="left", padx=(0, 5))
        
        tk.Button(button_frame, text="🔄 Update Code", command=update_office_code_gui,
                 bg=colors['warning'], fg="white", font=("Arial", font_sizes['card_description'], "bold"),
                 cursor="hand2", padx=10, pady=5).pack(side="left", padx=5)
        
        tk.Button(button_frame, text="🗑️ Delete", command=delete_office_gui,
                 bg=colors['accent'], fg="white", font=("Arial", font_sizes['card_description'], "bold"),
                 cursor="hand2", padx=10, pady=5).pack(side="left", padx=5)
        
        tk.Button(button_frame, text="🔄 Refresh", command=refresh_office_list,
                 bg=colors['info'], fg="white", font=("Arial", font_sizes['card_description'], "bold"),
                 cursor="hand2", padx=10, pady=5).pack(side="right")
        
        # Code Rotation Section - EXACTLY from legacy admin_gui.py
        tk.Label(parent, text="🔄 Automatic Code Rotation:",
                font=("Arial", font_sizes['button'], "bold"),
                fg=colors['dark'], bg=colors['white']).pack(anchor="w", pady=(20, 10))
        
        # Rotation buttons frame
        rotation_btn_frame = tk.Frame(parent, bg=colors['white'])
        rotation_btn_frame.pack(fill="x", pady=(0, 10))
        
        button_font_size = font_sizes['card_description']
        
        def weekly_rotation():
            """Weekly code rotation"""
            if tk.messagebox.askyesno("Weekly Code Rotation", 
                                  "Rotate ALL office codes?\n\n" +
                                  "This will:\n" +
                                  "• Generate new 4-digit codes for all offices\n" +
                                  "• Sync codes to Firebase automatically\n" +
                                  "• Old codes will become invalid\n\n" +
                                  "Continue?"):
                try:
                    from database.office_operation import rotate_all_office_codes_weekly
                    count = rotate_all_office_codes_weekly()
                    tk.messagebox.showinfo("Weekly Rotation Complete", 
                                       f"Successfully rotated codes for {count} offices!\n" +
                                       "All codes have been synced to Firebase.")
                    refresh_office_list()
                except Exception as e:
                    tk.messagebox.showerror("Error", f"Weekly rotation failed: {str(e)}")
        
        def daily_rotation():
            """Daily code rotation"""
            if tk.messagebox.askyesno("Daily Code Rotation", 
                                  "Rotate ALL office codes?\n\n" +
                                  "This will:\n" +
                                  "• Generate new 4-digit codes for all offices\n" +
                                  "• Sync codes to Firebase automatically\n" +
                                  "• Old codes will become invalid\n\n" +
                                  "Continue?"):
                try:
                    from database.office_operation import rotate_all_office_codes_daily
                    count = rotate_all_office_codes_daily()
                    tk.messagebox.showinfo("Daily Rotation Complete", 
                                       f"Successfully rotated codes for {count} offices!\n" +
                                       "All codes have been synced to Firebase.")
                    refresh_office_list()
                except Exception as e:
                    tk.messagebox.showerror("Error", f"Daily rotation failed: {str(e)}")
        
        def sync_firebase():
            """Sync all offices to Firebase"""
            if tk.messagebox.askyesno("Sync to Firebase", 
                                  "Sync all current office codes to Firebase?\n\n" +
                                  "This will upload all current codes to the online database."):
                try:
                    from database.office_operation import sync_all_offices_to_firebase
                    if sync_all_offices_to_firebase():
                        tk.messagebox.showinfo("Sync Complete", "All office codes synced to Firebase!")
                    else:
                        tk.messagebox.showerror("Sync Failed", "Failed to sync codes to Firebase!")
                except Exception as e:
                    tk.messagebox.showerror("Error", f"Firebase sync error: {str(e)}")
        
        # Rotation buttons - EXACTLY from legacy admin_gui.py
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
        
        return {
            'listbox': offices_listbox,
            'refresh': refresh_office_list
        }
    
    @staticmethod
    def create_users_display_window(parent_root, colors, font_sizes, admin_functions):
        """Create users display window with real data - FIXED to show actual users"""
        users_window = tk.Toplevel(parent_root)
        users_window.title("👥 Enrolled Users")
        users_window.configure(bg=colors['white'])
        
        # Calculate window size
        window_width = max(800, int(parent_root.winfo_screenwidth() * 0.8))
        window_height = max(600, int(parent_root.winfo_screenheight() * 0.8))
        
        # Center window
        x = (parent_root.winfo_screenwidth() - window_width) // 2
        y = (parent_root.winfo_screenheight() - window_height) // 2
        users_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Header
        header = tk.Frame(users_window, bg=colors['primary'],
                         height=max(60, int(window_height * 0.12)))
        header.pack(fill="x")
        header.pack_propagate(False)
        
        tk.Label(header, text="👥 Enrolled Users Database",
                font=("Arial", font_sizes['subtitle']), fg=colors['light'],
                bg=colors['primary']).pack(expand=True)
        
        # Load user data
        try:
            # Try to load from JSON file
            import json
            import os
            users_data = {}
            
            # Load fingerprint database
            fingerprint_file = "json_folder/fingerprint_database.json"
            if os.path.exists(fingerprint_file):
                with open(fingerprint_file, 'r') as f:
                    users_data = json.load(f)
            
            # Also try to get data from admin functions
            if admin_functions and 'view_enrolled' in admin_functions:
                try:
                    admin_functions['view_enrolled']()  # Call it for console output too
                except:
                    pass
            
            if not users_data:
                # No users found
                content_frame = tk.Frame(users_window, bg=colors['white'])
                content_frame.pack(fill="both", expand=True, padx=20, pady=20)
                
                tk.Label(content_frame, text="📭 No Users Enrolled",
                        font=("Arial", font_sizes['card_title'], "bold"), 
                        fg=colors['secondary'], bg=colors['white']).pack(pady=50)
                
                tk.Label(content_frame, text="No users have been enrolled in the system yet.",
                        font=("Arial", font_sizes['card_description']), 
                        fg=colors['secondary'], bg=colors['white']).pack()
            else:
                # Create scrollable content for users
                scrollable_frame = UIComponents.create_scrollable_container(users_window, colors)
                
                # Users list container
                users_frame = tk.Frame(scrollable_frame, bg=colors['white'])
                users_frame.pack(fill="both", expand=True, padx=15, pady=15)
                
                # Count users by type
                student_count = 0
                staff_count = 0
                admin_count = 0
                
                for user_id, info in users_data.items():
                    user_type = info.get('user_type', 'STUDENT')
                    if user_type == 'STUDENT':
                        student_count += 1
                    elif user_type == 'STAFF':
                        staff_count += 1
                    elif 'ADMIN' in user_type:
                        admin_count += 1
                
                # Stats bar
                stats_frame = tk.Frame(users_frame, bg=colors['light'])
                stats_frame.pack(fill="x", pady=(0, 20))
                
                stats_content = tk.Frame(stats_frame, bg=colors['light'])
                stats_content.pack(pady=10)
                
                for label, count, color in [
                    ("Total Users", len(users_data), colors['info']),
                    ("Students", student_count, colors['success']),
                    ("Staff", staff_count, colors['warning']),
                    ("Admins", admin_count, colors['accent'])
                ]:
                    stat_item = tk.Frame(stats_content, bg=colors['light'])
                    stat_item.pack(side="left", padx=20)
                    
                    tk.Label(stat_item, text=str(count),
                            font=("Arial", font_sizes['card_title'], "bold"),
                            fg=color, bg=colors['light']).pack()
                    tk.Label(stat_item, text=label,
                            font=("Arial", font_sizes['card_description']),
                            fg=colors['dark'], bg=colors['light']).pack()
                
                # User cards
                for slot_id, info in sorted(users_data.items(), key=lambda x: int(x[0]) if x[0].isdigit() else 999):
                    UIComponents.create_user_card(users_frame, slot_id, info, colors, font_sizes)
                        
        except Exception as e:
            # Error loading users
            content_frame = tk.Frame(users_window, bg=colors['white'])
            content_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            tk.Label(content_frame, text="❌ Error Loading Users",
                    font=("Arial", font_sizes['card_title'], "bold"), 
                    fg=colors['accent'], bg=colors['white']).pack(pady=20)
            
            tk.Label(content_frame, text=f"Error: {str(e)}",
                    font=("Arial", font_sizes['card_description']), 
                    fg=colors['secondary'], bg=colors['white']).pack()
        
        # Close button
        close_frame = tk.Frame(users_window, bg=colors['light'])
        close_frame.pack(fill="x", pady=10)
        
        tk.Button(close_frame, text="❌ Close", command=users_window.destroy,
                 bg=colors['dark'], fg="white", font=("Arial", font_sizes['button'], "bold"),
                 cursor="hand2", padx=20, pady=8).pack()
        
        return users_window
    
    @staticmethod
    def create_user_card(parent, slot_id, info, colors, font_sizes):
        """Create a user information card"""
        # Card container
        card_container = tk.Frame(parent, bg=colors['white'])
        card_container.pack(fill="x", padx=5, pady=3)
        
        # Card with border
        card = tk.Frame(card_container, bg=colors['light'], relief='solid', bd=1)
        card.pack(fill="x", padx=2, pady=2)
        
        # Content padding
        content = tk.Frame(card, bg=colors['light'])
        content.pack(fill="x", padx=15, pady=10)
        
        # Header row with slot and type
        header_row = tk.Frame(content, bg=colors['light'])
        header_row.pack(fill="x", pady=(0, 8))
        
        # Left side - Slot and name
        left_info = tk.Frame(header_row, bg=colors['light'])
        left_info.pack(side="left", fill="x", expand=True)
        
        # Slot number and name
        name_text = f"Slot #{slot_id}: {info.get('name', 'N/A')}"
        tk.Label(left_info, text=name_text,
                font=("Arial", font_sizes['card_title'], "bold"),
                fg=colors['dark'], bg=colors['light']).pack(anchor="w")
        
        # User type
        user_type = info.get('user_type', 'STUDENT')
        type_color = colors['success'] if user_type == 'STUDENT' else colors['info'] if user_type == 'STAFF' else colors['accent']
        
        tk.Label(left_info, text=f"Type: {user_type}",
                font=("Arial", font_sizes['card_description'], "bold"),
                fg=type_color, bg=colors['light']).pack(anchor="w")
        
        # Details row
        details_frame = tk.Frame(content, bg=colors['light'])
        details_frame.pack(fill="x")
        
        # Left column
        left_col = tk.Frame(details_frame, bg=colors['light'])
        left_col.pack(side="left", fill="x", expand=True)
        
        # Right column  
        right_col = tk.Frame(details_frame, bg=colors['light'])
        right_col.pack(side="right", fill="x", expand=True)
        
        # Add details based on user type
        if user_type == 'STUDENT':
            UIComponents.add_detail_row(left_col, "Student ID:", info.get('student_id', 'N/A'), colors, font_sizes)
            UIComponents.add_detail_row(left_col, "Course:", info.get('course', 'N/A'), colors, font_sizes)
        elif user_type == 'STAFF':
            UIComponents.add_detail_row(left_col, "Staff No:", info.get('staff_no', 'N/A'), colors, font_sizes)
            UIComponents.add_detail_row(left_col, "Role:", info.get('staff_role', 'N/A'), colors, font_sizes)
        
        UIComponents.add_detail_row(right_col, "License:", info.get('license_number', 'N/A'), colors, font_sizes)
        UIComponents.add_detail_row(right_col, "Plate:", info.get('plate_number', 'N/A'), colors, font_sizes)
    
    @staticmethod
    def add_detail_row(parent, label, value, colors, font_sizes):
        """Add a detail row to user card"""
        row = tk.Frame(parent, bg=colors['light'])
        row.pack(fill="x", pady=1)
        
        tk.Label(row, text=label, font=("Arial", font_sizes['card_description']),
                fg=colors['secondary'], bg=colors['light'], width=12, anchor="w").pack(side="left")
        tk.Label(row, text=str(value), font=("Arial", font_sizes['card_description'], "bold"),
                fg=colors['dark'], bg=colors['light']).pack(side="left", anchor="w")
    
    @staticmethod
    def create_time_records_window(parent_root, colors, font_sizes, admin_functions):
        """Create time records display window with real data - FIXED to show actual records"""
        records_window = tk.Toplevel(parent_root)
        records_window.title("🕒 Time Records")
        records_window.configure(bg=colors['white'])
        
        # Calculate window size
        window_width = max(900, int(parent_root.winfo_screenwidth() * 0.9))
        window_height = max(650, int(parent_root.winfo_screenheight() * 0.85))
        
        # Center window
        x = (parent_root.winfo_screenwidth() - window_width) // 2
        y = (parent_root.winfo_screenheight() - window_height) // 2
        records_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Header
        header = tk.Frame(records_window, bg=colors['secondary'],
                         height=max(60, int(window_height * 0.12)))
        header.pack(fill="x")
        header.pack_propagate(False)
        
        tk.Label(header, text="🕒 Time Tracking Records",
                font=("Arial", font_sizes['subtitle']), fg=colors['light'],
                bg=colors['secondary']).pack(expand=True)
        
        # Load time records data
        try:
            records_data = []
            
            # Try to get records from admin functions first
            if admin_functions and 'get_time_records' in admin_functions:
                try:
                    records_data = admin_functions['get_time_records']()
                    if not isinstance(records_data, list):
                        records_data = []
                except:
                    pass
            
            # If no records from function, try to load from database directly
            if not records_data:
                try:
                    from database.db_operations import get_all_time_records
                    records_data = get_all_time_records()
                except:
                    records_data = []
            
            if not records_data:
                # No records found
                content_frame = tk.Frame(records_window, bg=colors['white'])
                content_frame.pack(fill="both", expand=True, padx=20, pady=20)
                
                tk.Label(content_frame, text="📭 No Time Records",
                        font=("Arial", font_sizes['card_title'], "bold"), 
                        fg=colors['secondary'], bg=colors['white']).pack(pady=50)
                
                tk.Label(content_frame, text="No time tracking records found in the system.",
                        font=("Arial", font_sizes['card_description']), 
                        fg=colors['secondary'], bg=colors['white']).pack()
            else:
                # Create table for records
                table_frame = tk.Frame(records_window, bg=colors['white'])
                table_frame.pack(fill="both", expand=True, padx=15, pady=15)
                
                # Configure treeview style
                style = ttk.Style()
                style.theme_use('clam')
                style.configure('Treeview', 
                              background=colors['white'],
                              fieldbackground=colors['white'],
                              borderwidth=0,
                              font=('Arial', max(9, int(font_sizes['card_description']))))
                style.configure('Treeview.Heading', 
                              background=colors['light'],
                              font=('Arial', max(10, int(font_sizes['card_description'])), 'bold'))
                style.map('Treeview', background=[('selected', colors['info'])])
                
                # Create treeview
                tree = ttk.Treeview(table_frame, 
                                   columns=('Date', 'Time', 'User_ID', 'Name', 'Type', 'Action'), 
                                   show='headings', height=20)
                
                # Configure columns
                tree.column('Date', width=100, anchor='center')
                tree.column('Time', width=80, anchor='center')  
                tree.column('User_ID', width=80, anchor='center')
                tree.column('Name', width=200, anchor='w')
                tree.column('Type', width=80, anchor='center')
                tree.column('Action', width=60, anchor='center')
                
                # Configure headings
                tree.heading('Date', text='Date')
                tree.heading('Time', text='Time')
                tree.heading('User_ID', text='User ID')
                tree.heading('Name', text='Name')
                tree.heading('Type', text='Type')
                tree.heading('Action', text='Action')
                
                # Add records to tree
                for i, record in enumerate(records_data[-100:]):  # Show last 100 records
                    # Handle different record formats
                    if isinstance(record, dict):
                        date = record.get('date', 'N/A')
                        time = record.get('time', 'N/A')
                        user_id = record.get('user_id', record.get('student_id', 'N/A'))
                        name = record.get('user_name', record.get('student_name', 'N/A'))
                        user_type = record.get('user_type', 'STUDENT')
                        action = record.get('action', record.get('status', 'N/A'))
                    else:
                        # Handle tuple format if needed
                        date = str(record[0]) if len(record) > 0 else 'N/A'
                        time = str(record[1]) if len(record) > 1 else 'N/A'
                        user_id = str(record[2]) if len(record) > 2 else 'N/A'
                        name = str(record[3]) if len(record) > 3 else 'N/A'
                        user_type = str(record[4]) if len(record) > 4 else 'STUDENT'
                        action = str(record[5]) if len(record) > 5 else 'N/A'
                    
                    # Color code by action
                    tag = 'in' if action.upper() == 'IN' else 'out'
                    values = (date, time, user_id, name, user_type, action)
                    tree.insert('', 'end', values=values, tags=(tag,))
                
                # Configure tags for coloring
                tree.tag_configure('in', foreground=colors['success'])
                tree.tag_configure('out', foreground=colors['accent'])
                
                # Scrollbar for tree
                tree_scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=tree.yview)
                tree.configure(yscrollcommand=tree_scrollbar.set)
                
                # Pack tree and scrollbar
                tree.pack(side='left', fill='both', expand=True)
                tree_scrollbar.pack(side='right', fill='y')
                
                # Summary info
                summary_frame = tk.Frame(records_window, bg=colors['light'])
                summary_frame.pack(fill="x", padx=15, pady=10)
                
                tk.Label(summary_frame, text=f"Total Records: {len(records_data)} (Showing last 100)",
                        font=("Arial", font_sizes['card_description']), 
                        fg=colors['dark'], bg=colors['light']).pack()
                        
        except Exception as e:
            # Error loading records
            content_frame = tk.Frame(records_window, bg=colors['white'])
            content_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            tk.Label(content_frame, text="❌ Error Loading Records",
                    font=("Arial", font_sizes['card_title'], "bold"), 
                    fg=colors['accent'], bg=colors['white']).pack(pady=20)
            
            tk.Label(content_frame, text=f"Error: {str(e)}",
                    font=("Arial", font_sizes['card_description']), 
                    fg=colors['secondary'], bg=colors['white']).pack()
        
        # Close button
        close_frame = tk.Frame(records_window, bg=colors['light'])
        close_frame.pack(fill="x", pady=10)
        
        tk.Button(close_frame, text="❌ Close", command=records_window.destroy,
                 bg=colors['dark'], fg="white", font=("Arial", font_sizes['button'], "bold"),
                 cursor="hand2", padx=20, pady=8).pack()
        
        return records_window
