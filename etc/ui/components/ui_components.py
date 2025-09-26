# ui/ui_components.py - Reusable UI Components for MotorPass System
# KISS principle: Simple, reusable UI functions that don't change design

import tkinter as tk
from tkinter import ttk

class UIComponents:
    """Reusable UI components for consistent design across all GUIs"""
    
    @staticmethod
    def create_function_card(parent, icon, title, description, command, color, 
                           screen_width, display_size, colors, has_access=True, function_name=None):
        """Create an enhanced function card with access control - RESPONSIVE
        
        Args:
            parent: Parent widget
            icon: Emoji icon for the card
            title: Card title text
            description: Card description text
            command: Function to call when clicked
            color: Primary color for the card
            screen_width: Screen width for responsive calculations
            display_size: Display size for font calculations  
            colors: Color dictionary
            has_access: Whether user has access to this function
            function_name: Name of function for access control
        """
        # Adjust colors for restricted access
        if not has_access:
            color = '#CCCCCC'
            
        # Card frame with shadow - responsive spacing
        card_spacing = max(6, int(screen_width * 0.008))
        card_container = tk.Frame(parent, bg=colors['white'])
        card_container.pack(side="left", fill="both", expand=True, padx=card_spacing)
        
        # Shadow effect
        shadow = tk.Frame(card_container, bg='#D5D5D5')
        shadow.place(x=2, y=2, relwidth=1, relheight=1)
        
        # Main card
        card = tk.Frame(card_container, bg=colors['light'], relief='flat', bd=0)
        card.pack(fill="both", expand=True)
        
        # Content with responsive padding
        content_padding = max(12, int(display_size / 70))
        content = tk.Frame(card, bg=colors['light'])
        content.pack(fill="both", expand=True, padx=content_padding, pady=content_padding)
        
        # Icon - responsive size
        icon_size = max(24, int(display_size / 35))
        icon_label = tk.Label(content, text=icon, font=("Arial", icon_size), 
                             fg=color, bg=colors['light'])
        icon_label.pack(pady=(0, 8))
        
        # Title - responsive font
        title_size = max(11, int(display_size / 75))
        title_label = tk.Label(content, text=title, font=("Arial", title_size, "bold"), 
                              fg=colors['dark'], bg=colors['light'])
        title_label.pack(pady=(0, 4))
        
        # Description - responsive font
        desc_size = max(8, int(display_size / 100))
        desc_label = tk.Label(content, text=description, font=("Arial", desc_size), 
                             fg=colors['secondary'], bg=colors['light'], 
                             wraplength=max(120, int(display_size / 8)))
        desc_label.pack()
        
        # Make card clickable if user has access
        if has_access and command:
            def on_click(event=None):
                if callable(command):
                    command()
            
            # Bind click events to all card components
            for widget in [card_container, shadow, card, content, icon_label, title_label, desc_label]:
                widget.bind("<Button-1>", on_click)
                widget.configure(cursor="hand2")
                
            # Add hover effects
            def on_enter(event=None):
                card.configure(bg='#F8F9FA')
                content.configure(bg='#F8F9FA') 
                icon_label.configure(bg='#F8F9FA')
                title_label.configure(bg='#F8F9FA')
                desc_label.configure(bg='#F8F9FA')
                
            def on_leave(event=None):
                card.configure(bg=colors['light'])
                content.configure(bg=colors['light'])
                icon_label.configure(bg=colors['light'])
                title_label.configure(bg=colors['light'])
                desc_label.configure(bg=colors['light'])
                
            # Bind hover events
            for widget in [card_container, shadow, card, content, icon_label, title_label, desc_label]:
                widget.bind("<Enter>", on_enter)
                widget.bind("<Leave>", on_leave)
        
        return card_container
    
    @staticmethod
    def create_stat_card(parent, icon, label, value, color, colors, display_size, spacing=10):
        """Create a statistics card - RESPONSIVE
        
        Args:
            parent: Parent widget
            icon: Emoji icon
            label: Stat label text
            value: Stat value
            color: Color for the value text
            colors: Color dictionary
            display_size: Display size for calculations
            spacing: Vertical spacing
        """
        card = tk.Frame(parent, bg=colors['dark'])
        card.pack(fill="x", padx=12, pady=spacing)
        
        # Content frame with responsive padding
        content_padding = max(8, int(display_size / 100))
        content = tk.Frame(card, bg=colors['dark'])
        content.pack(fill="x", padx=content_padding, pady=content_padding)
        
        # Icon and label with responsive fonts
        top_row = tk.Frame(content, bg=colors['dark'])
        top_row.pack(fill="x")
        
        stat_label_size = max(9, int(display_size / 90))
        stat_value_size = max(16, int(display_size / 50))
        
        tk.Label(top_row, text=f"{icon} {label}", 
                font=("Arial", stat_label_size), fg=colors['light'], 
                bg=colors['dark']).pack(side="left")
        
        # Value
        tk.Label(content, text=str(value), 
                font=("Arial", stat_value_size, "bold"), fg=color, 
                bg=colors['dark']).pack(anchor="w", pady=(3, 0))
        
        return card
    
    @staticmethod
    def create_modern_user_card(parent, slot_id, info, colors, display_size):
        """Create a modern user information card - RESPONSIVE
        
        Args:
            parent: Parent widget
            slot_id: User slot ID
            info: User information dictionary
            colors: Color dictionary
            display_size: Display size for calculations
        """
        # Card container with shadow
        card_container = tk.Frame(parent, bg=colors['white'])
        card_container.pack(fill="x", padx=8, pady=6)
        
        # Card
        card = tk.Frame(card_container, bg=colors['light'], relief='flat', bd=0)
        card.pack(fill="x", padx=2, pady=2)
        
        # Type indicator
        type_color = colors['success'] if info.get('user_type') == 'STUDENT' else colors['info']
        type_bar = tk.Frame(card, bg=type_color, width=5)
        type_bar.pack(side="left", fill="y")
        
        # Content with responsive padding
        padding_x = max(15, int(display_size / 50))
        padding_y = max(10, int(display_size / 80))
        content = tk.Frame(card, bg=colors['light'])
        content.pack(side="left", fill="both", expand=True, padx=padding_x, pady=padding_y)
        
        # Header row
        header_row = tk.Frame(content, bg=colors['light'])
        header_row.pack(fill="x", pady=(0, 8))
        
        # Name and type - responsive fonts
        name_font_size = max(12, int(display_size / 70))
        type_font_size = max(8, int(display_size / 100))
        
        name_frame = tk.Frame(header_row, bg=colors['light'])
        name_frame.pack(side="left")
        
        tk.Label(name_frame, text=info.get('name', 'N/A'), 
                font=("Arial", name_font_size, "bold"), fg=colors['dark'], 
                bg=colors['light']).pack(anchor="w")
        
        type_text = f"{info.get('user_type', 'UNKNOWN')} • Slot #{slot_id}"
        tk.Label(name_frame, text=type_text, 
                font=("Arial", type_font_size), fg=colors['secondary'], 
                bg=colors['light']).pack(anchor="w")
        
        return card_container
    
    @staticmethod
    def create_menu_card_layout(parent, cards_data, colors, screen_width, screen_height, 
                               display_size, is_square_display, has_access_func):
        """Create responsive menu card layout
        
        Args:
            parent: Parent widget
            cards_data: List of tuples (icon, title, description, command, color, function_name)
            colors: Color dictionary
            screen_width, screen_height: Screen dimensions
            display_size: Display size for calculations
            is_square_display: Boolean for display type
            has_access_func: Function to check access permissions
        """
        # Title with responsive font
        title_font_size = max(16, int(display_size / 50))
        title_padding = max(15, int(screen_height * 0.02))
        
        tk.Label(parent, text="SYSTEM FUNCTIONS", 
                font=("Arial", title_font_size, "bold"), fg=colors['primary'], 
                bg=colors['white']).pack(pady=(title_padding, title_padding))
        
        # Cards container with responsive padding
        cards_padding = max(20, int(screen_width * 0.03))
        cards_container = tk.Frame(parent, bg=colors['white'])
        cards_container.pack(fill="both", expand=True, padx=cards_padding)
        
        # Responsive card layout
        if is_square_display:
            # For square displays, use 2x4 grid (2 columns, 4 rows)
            rows = [tk.Frame(cards_container, bg=colors['white']) for _ in range(4)]
            for i, row in enumerate(rows):
                row.pack(fill="x", pady=(0, 12))
            
            # Arrange cards in 2x4 grid
            for i, card_data in enumerate(cards_data):
                row_index = i // 2
                if row_index < len(rows):
                    icon, title, description, command, color, function_name = card_data
                    has_access = has_access_func(function_name) if function_name else True
                    UIComponents.create_function_card(
                        rows[row_index], icon, title, description, command, color,
                        screen_width, display_size, colors, has_access, function_name
                    )
        else:
            # For wider displays, use 3 rows
            row1 = tk.Frame(cards_container, bg=colors['white'])
            row1.pack(fill="x", pady=(0, 15))
            
            row2 = tk.Frame(cards_container, bg=colors['white'])
            row2.pack(fill="x", pady=(0, 15))
            
            row3 = tk.Frame(cards_container, bg=colors['white'])
            row3.pack(fill="x")
            
            rows = [row1, row2, row3]
            
            # Distribute cards across rows
            cards_per_row = len(cards_data) // 3 + (1 if len(cards_data) % 3 > 0 else 0)
            
            for i, card_data in enumerate(cards_data):
                row_index = i // cards_per_row if cards_per_row > 0 else 0
                row_index = min(row_index, len(rows) - 1)  # Ensure we don't exceed available rows
                
                icon, title, description, command, color, function_name = card_data
                has_access = has_access_func(function_name) if function_name else True
                UIComponents.create_function_card(
                    rows[row_index], icon, title, description, command, color,
                    screen_width, display_size, colors, has_access, function_name
                )
    
    @staticmethod
    def create_scrollable_container(parent, colors):
        """Create a scrollable container with mouse wheel support
        
        Args:
            parent: Parent widget
            colors: Color dictionary
            
        Returns:
            scrollable_frame: Frame where content should be added
        """
        # Container
        container = tk.Frame(parent, bg=colors['white'])
        container.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Canvas and scrollbar
        canvas = tk.Canvas(container, bg=colors['white'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=colors['white'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Bind mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        # Bind events to enable scrolling
        for widget in [canvas, container, parent]:
            widget.bind("<MouseWheel>", _on_mousewheel)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    @staticmethod
    def create_office_management_section(parent, colors, font_sizes, refresh_callback=None):
        """Create complete office management section with rotation functions
        
        Args:
            parent: Parent widget
            colors: Color dictionary  
            font_sizes: Font sizes dictionary
            refresh_callback: Function to refresh office list
            
        Returns:
            dict: Contains listbox and refresh function
        """
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
        
        # Office listbox
        offices_listbox = tk.Listbox(parent, height=6,
                                    font=("Arial", font_sizes['card_description']))
        offices_listbox.pack(fill="x", pady=(0, 10))
        
        def refresh_office_list():
            offices_listbox.delete(0, tk.END)
            offices = get_all_offices()
            for office in offices:
                offices_listbox.insert(tk.END, f"{office['office_name']} (Code: {office['office_code']})")
        
        def add_new_office():
            import tkinter.simpledialog
            office_name = tkinter.simpledialog.askstring("Add Office", "Enter office name:")
            if office_name and office_name.strip():
                if add_office(office_name.strip()):
                    tk.messagebox.showinfo("Success", f"Office '{office_name}' added successfully!")
                    refresh_office_list()
                else:
                    tk.messagebox.showerror("Error", "Failed to add office!")
        
        def update_office_code_gui():
            import tkinter.simpledialog
            selection = offices_listbox.curselection()
            if not selection:
                tk.messagebox.showwarning("Warning", "Please select an office first!")
                return
            
            office_text = offices_listbox.get(selection[0])
            office_name = office_text.split(" (Code:")[0]
            current_code = office_text.split("Code: ")[1].replace(")", "")
            
            new_code = tkinter.simpledialog.askstring("Update Security Code",
                                               f"Current code for '{office_name}': {current_code}\n\nEnter new 4-digit code:")
            if new_code and new_code.strip():
                if update_office_code(office_name, new_code.strip()):
                    tk.messagebox.showinfo("Success", f"Security code updated for '{office_name}'!")
                    refresh_office_list()
                else:
                    tk.messagebox.showerror("Error", "Failed to update code!")
        
        def delete_office_gui():
            selection = offices_listbox.curselection()
            if not selection:
                tk.messagebox.showwarning("Warning", "Please select an office first!")
                return
            
            office_text = offices_listbox.get(selection[0])
            office_name = office_text.split(" (Code:")[0]
            
            if tk.messagebox.askyesno("Confirm Delete", f"Delete office '{office_name}'?"):
                if delete_office(office_name):
                    tk.messagebox.showinfo("Success", f"Office '{office_name}' deleted!")
                    refresh_office_list()
                else:
                    tk.messagebox.showerror("Error", "Failed to delete office!")
        
        # Office management buttons
        btn_frame = tk.Frame(parent, bg=colors['white'])
        btn_frame.pack(fill="x", pady=(0, 15))
        
        tk.Button(btn_frame, text="➕ Add Office", command=add_new_office,
                 bg=colors['success'], fg="white", font=("Arial", font_sizes['button'], "bold"),
                 cursor="hand2", padx=10, pady=5).pack(side="left", padx=3)
        
        tk.Button(btn_frame, text="🔄 Update Code", command=update_office_code_gui,
                 bg=colors['warning'], fg="white", font=("Arial", font_sizes['button'], "bold"),
                 cursor="hand2", padx=10, pady=5).pack(side="left", padx=3)
        
        tk.Button(btn_frame, text="🗑️ Delete Office", command=delete_office_gui,
                 bg=colors['accent'], fg="white", font=("Arial", font_sizes['button'], "bold"),
                 cursor="hand2", padx=10, pady=5).pack(side="left", padx=3)
        
        # ROTATION SECTION - THE REUSABLE FUNCTIONS
        UIComponents.create_rotation_section(parent, colors, font_sizes, refresh_office_list)
        
        # Load initial data
        refresh_office_list()
        
        return {
            'listbox': offices_listbox,
            'refresh': refresh_office_list
        }
    
    @staticmethod  
    def create_rotation_section(parent, colors, font_sizes, refresh_callback):
        """Create the rotation section with all rotation functions
        
        Args:
            parent: Parent widget
            colors: Color dictionary
            font_sizes: Font sizes dictionary  
            refresh_callback: Function to refresh office list after rotation
        """
        # Separator
        separator = tk.Frame(parent, bg=colors['light'], height=2)
        separator.pack(fill="x", pady=10)
        
        # Rotation section
        rotation_section = tk.Frame(parent, bg=colors['white'])
        rotation_section.pack(fill="x", pady=15)
        
        tk.Label(rotation_section, text="🔄 Code Rotation (System Maintenance)", 
                 font=("Arial", font_sizes['button'], "bold"), 
                 bg=colors['white'], fg=colors['primary']).pack(pady=(0, 5))
        
        tk.Label(rotation_section, text="Rotate all office codes at once - codes automatically sync to Firebase",
                 font=("Arial", font_sizes['card_description']), 
                 fg=colors['secondary'], bg=colors['white']).pack(pady=(0, 10))
        
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
                    refresh_callback()
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
                    refresh_callback()
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
        
        # Rotation buttons
        rotation_buttons = tk.Frame(rotation_section, bg=colors['white'])
        rotation_buttons.pack(fill="x", pady=(0, 15))
        
        tk.Button(rotation_buttons, text="📅 Weekly Rotation", 
                 font=("Arial", font_sizes['button']),
                 bg="#3498DB", fg="white", cursor="hand2", width=15,
                 padx=10, pady=5, command=weekly_rotation).pack(side="left", padx=(0, 5))
        
        tk.Button(rotation_buttons, text="🗓️ Daily Rotation", 
                 font=("Arial", font_sizes['button']),
                 bg="#E67E22", fg="white", cursor="hand2", width=15,
                 padx=10, pady=5, command=daily_rotation).pack(side="left", padx=5)
        
        tk.Button(rotation_buttons, text="🔥 Sync Firebase", 
                 font=("Arial", font_sizes['button']),
                 bg="#27AE60", fg="white", cursor="hand2", width=15,
                 padx=10, pady=5, command=sync_firebase).pack(side="right", padx=(5, 0))
