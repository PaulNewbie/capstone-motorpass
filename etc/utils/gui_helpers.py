# utils/gui_helpers.py - Fixed GUI Helper Functions
# this is currenltly file of gui_helpers.py

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import threading
import os

def show_results_gui(title, image=None, text="", success=True, details=None):
    """Display results in a GUI window"""
    # Create results window
    results_window = tk.Toplevel()
    results_window.title(title)
    results_window.geometry("800x600")
    results_window.configure(bg="#FFFFFF")
    
    # Center the window
    results_window.update_idletasks()
    x = (results_window.winfo_screenwidth() // 2) - (800 // 2)
    y = (results_window.winfo_screenheight() // 2) - (600 // 2)
    results_window.geometry(f"800x600+{x}+{y}")
    
    # Main frame
    main_frame = tk.Frame(results_window, bg="#FFFFFF")
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Title label
    title_color = "#008000" if success else "#FF0000"
    title_label = tk.Label(main_frame, 
                          text=title,
                          font=("Arial", 18, "bold"),
                          fg=title_color,
                          bg="#FFFFFF")
    title_label.pack(pady=(0, 20))
    
    # Text message
    if text:
        text_label = tk.Label(main_frame,
                             text=text,
                             font=("Arial", 12),
                             fg="#333333",
                             bg="#FFFFFF",
                             wraplength=700,
                             justify="center")
        text_label.pack(pady=(0, 20))
    
    # Details section
    if details:
        details_frame = tk.LabelFrame(main_frame, 
                                    text="Details",
                                    font=("Arial", 12, "bold"),
                                    fg="#333333",
                                    bg="#FFFFFF")
        details_frame.pack(fill="x", pady=(0, 20))
        
        for key, value in details.items():
            detail_text = f"{key}: {value}"
            detail_label = tk.Label(details_frame,
                                  text=detail_text,
                                  font=("Arial", 10),
                                  fg="#333333",
                                  bg="#FFFFFF",
                                  anchor="w")
            detail_label.pack(fill="x", padx=10, pady=2)
    
    # OK button
    button_frame = tk.Frame(main_frame, bg="#FFFFFF")
    button_frame.pack(fill="x", pady=(20, 0))
    
    ok_button = tk.Button(button_frame,
                         text="OK",
                         font=("Arial", 12, "bold"),
                         bg="#4CAF50",
                         fg="white",
                         padx=30,
                         pady=10,
                         command=results_window.destroy)
    ok_button.pack(side="right", padx=(10, 0))
    
    # Make window modal
    results_window.transient()
    results_window.grab_set()
    results_window.wait_window()

def get_guest_info_gui(detected_name=""):
    """Enhanced guest info GUI with office buttons, mouse support, AND retake functionality"""
    # Try to import office operations
    try:
        from database.office_operation import get_all_offices
        offices_data = get_all_offices()
        use_office_buttons = True
    except ImportError:
        offices_data = []
        use_office_buttons = False
    
    # Create window
    info_window = tk.Toplevel()
    info_window.title("Guest Registration")
    
    if use_office_buttons and offices_data:
        info_window.geometry("600x500")
    else:
        info_window.geometry("500x400")
    
    info_window.configure(bg="#FFFFFF")
    
    # Center window
    info_window.update_idletasks()
    x = (info_window.winfo_screenwidth() // 2) - (300 if use_office_buttons else 250)
    y = (info_window.winfo_screenheight() // 2) - (250 if use_office_buttons else 200)
    
    if use_office_buttons and offices_data:
        info_window.geometry(f"600x500+{x}+{y}")
    else:
        info_window.geometry(f"500x400+{x}+{y}")
    
    # Main frame
    main_frame = tk.Frame(info_window, bg="#FFFFFF")
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Title
    title_label = tk.Label(main_frame, text="🎫 GUEST REGISTRATION", 
                          font=("Arial", 18, "bold"), fg="#333333", bg="#FFFFFF")
    title_label.pack(pady=(0, 20))
    
    # Name field
    tk.Label(main_frame, text="Full Name:", font=("Arial", 10, "bold"), bg="#FFFFFF").pack(anchor="w", pady=(0, 5))
    name_entry = tk.Entry(main_frame, font=("Arial", 12), width=50)
    name_entry.pack(pady=(0, 15), fill="x")
    if detected_name:
        name_entry.insert(0, detected_name)
    
    # Plate number field
    tk.Label(main_frame, text="Plate Number:", font=("Arial", 10, "bold"), bg="#FFFFFF").pack(anchor="w", pady=(0, 5))
    plate_entry = tk.Entry(main_frame, font=("Arial", 12), width=50)
    plate_entry.pack(pady=(0, 20), fill="x")
    
    # Office selection
    tk.Label(main_frame, text="Select Office to Visit:", font=("Arial", 10, "bold"), bg="#FFFFFF").pack(anchor="w", pady=(0, 10))
    
    selected_office = tk.StringVar()
    
    if use_office_buttons and offices_data:
        # OFFICE BUTTONS (Enhanced with mouse support)
        office_frame = tk.Frame(main_frame, bg="#FFFFFF")
        office_frame.pack(fill="x", pady=(0, 20))
        
        # Create buttons in grid layout
        buttons_per_row = 3
        button_widgets = []
        
        for i, office in enumerate(offices_data):
            row = i // buttons_per_row
            col = i % buttons_per_row
            
            def make_select_office(office_name):
                def select_office():
                    selected_office.set(office_name)
                    # Update button colors
                    for btn_widget in button_widgets:
                        if btn_widget['text'] == office_name:
                            btn_widget.config(bg="#4CAF50", fg="white")
                        else:
                            btn_widget.config(bg="#f0f0f0", fg="black")
                return select_office
            
            btn = tk.Button(office_frame, text=office['office_name'], 
                           font=("Arial", 9), width=18, height=2,
                           bg="#f0f0f0", fg="black", relief="raised", bd=2,
                           cursor="hand2",  # Add cursor
                           command=make_select_office(office['office_name']))
            btn.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
            button_widgets.append(btn)
            
            # Add hover effects
            def on_enter(e, button=btn):
                if button['bg'] != "#4CAF50":  # Don't change if selected
                    button.config(bg="#e0e0e0")
            
            def on_leave(e, button=btn):
                if button['bg'] != "#4CAF50":  # Don't change if selected
                    button.config(bg="#f0f0f0")
            
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)
        
        # Configure grid weights
        for i in range(buttons_per_row):
            office_frame.grid_columnconfigure(i, weight=1)
    
    else:
        # FALLBACK DROPDOWN (if office buttons not available)
        office_var = tk.StringVar(value="CSS Office")
        office_combo = ttk.Combobox(main_frame, 
                                   textvariable=office_var,
                                   font=("Arial", 10),
                                   width=47,
                                   values=[
                                       "CSS Office",
                                       "Registrar Office", 
                                       "Cashier Office",
                                       "Dean's Office",
                                       "Library",
                                       "IT Office",
                                       "Main Office",
                                       "Other"
                                   ])
        office_combo.pack(pady=(0, 20), fill="x")
        selected_office = office_var  # Use the same variable
    
    result = [None]
    
    def submit_info():
        name = name_entry.get().strip()
        plate = plate_entry.get().strip().upper()
        office = selected_office.get()
        
        if not name:
            messagebox.showerror("Error", "Name is required!")
            name_entry.focus()
            return
        if not plate:
            messagebox.showerror("Error", "Plate number is required!")
            plate_entry.focus()
            return
        if not office:
            messagebox.showerror("Error", "Please select an office to visit!")
            return
            
        result[0] = {
            'name': name,
            'plate_number': plate,
            'office': office
        }
        info_window.destroy()
    
    def cancel():
        result[0] = None
        info_window.destroy()
    
    def retake():
        """RESTORED retake function"""
        result[0] = 'retake'
        info_window.destroy()
    
    # Bottom buttons
    button_frame = tk.Frame(main_frame, bg="#FFFFFF")
    button_frame.pack(fill="x", pady=(20, 0))
    
    # Cancel button (left)
    cancel_button = tk.Button(button_frame, text="❌ Cancel", 
                             font=("Arial", 10, "bold"), bg="#FF6B6B", fg="white",
                             padx=20, pady=8, command=cancel, cursor="hand2")
    cancel_button.pack(side="left")
    
    # RESTORED RETAKE BUTTON (center)
    retake_button = tk.Button(button_frame, text="📷 Retake License", 
                             font=("Arial", 10, "bold"), bg="#3498DB", fg="white",
                             padx=20, pady=8, command=retake, cursor="hand2")
    retake_button.pack(side="left", padx=(10, 0))
    
    # Submit button (right)
    submit_button = tk.Button(button_frame, text="✅ Register Guest", 
                             font=("Arial", 10, "bold"), bg="#4CAF50", fg="white",
                             padx=20, pady=8, command=submit_info, cursor="hand2")
    submit_button.pack(side="right")
    
    # Keyboard support
    def on_key_press(event):
        if event.keysym == 'Return':
            submit_info()
        elif event.keysym == 'Escape':
            cancel()
    
    info_window.bind('<Key>', on_key_press)
    info_window.focus_set()
    
    # Tab navigation
    name_entry.bind('<Tab>', lambda e: plate_entry.focus())
    plate_entry.bind('<Tab>', lambda e: submit_button.focus())
    
    # Window close handler
    def on_window_close():
        result[0] = None
        info_window.destroy()
    
    info_window.protocol("WM_DELETE_WINDOW", on_window_close)
    
    # Make window modal
    info_window.transient()
    info_window.grab_set()
    
    # Focus on name entry
    name_entry.focus()
    
    info_window.wait_window()
    
    return result[0]
     
def updated_guest_office_gui(guest_name, current_office):
    """Get updated office information for returning guest"""
    # Create update window
    update_window = tk.Toplevel()
    update_window.title("Update Guest Office")
    update_window.geometry("400x300")
    update_window.configure(bg="#FFFFFF")
    
    # Center the window
    update_window.update_idletasks()
    x = (update_window.winfo_screenwidth() // 2) - (200)
    y = (update_window.winfo_screenheight() // 2) - (150)
    update_window.geometry(f"400x300+{x}+{y}")
    
    # Main frame
    main_frame = tk.Frame(update_window, bg="#FFFFFF")
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Title
    title_label = tk.Label(main_frame,
                          text="Update Office Visit",
                          font=("Arial", 16, "bold"),
                          fg="#333333",
                          bg="#FFFFFF")
    title_label.pack(pady=(0, 20))
    
    # Guest info
    info_label = tk.Label(main_frame,
                         text=f"Returning Guest: {guest_name}",
                         font=("Arial", 12, "bold"),
                         fg="#0066CC",
                         bg="#FFFFFF")
    info_label.pack(pady=(0, 10))
    
    current_label = tk.Label(main_frame,
                           text=f"Previous Office: {current_office}",
                           font=("Arial", 10),
                           fg="#666666",
                           bg="#FFFFFF")
    current_label.pack(pady=(0, 20))
    
    # Office selection
    tk.Label(main_frame, text="Select Office to Visit:", font=("Arial", 10, "bold"), bg="#FFFFFF").pack(anchor="w", pady=(0, 5))
    
    office_var = tk.StringVar(value=current_office)
    office_combo = ttk.Combobox(main_frame, 
                               textvariable=office_var,
                               font=("Arial", 10),
                               width=35,
                               values=[
                                   "CSS Office",
                                   "Registrar Office", 
                                   "Cashier Office",
                                   "Dean's Office",
                                   "Library",
                                   "IT Office",
                                   "Main Office",
                                   "Other"
                               ])
    office_combo.pack(pady=(0, 20), fill="x")
    
    result = [None]
    
    def update_info():
        office = office_var.get().strip()
        if not office:
            office = current_office
            
        result[0] = {
            'name': guest_name,
            'office': office
        }
        update_window.destroy()
    
    def cancel():
        update_window.destroy()
    
    # Buttons
    button_frame = tk.Frame(main_frame, bg="#FFFFFF")
    button_frame.pack(fill="x", pady=(10, 0))
    
    cancel_button = tk.Button(button_frame,
                             text="Cancel",
                             font=("Arial", 10, "bold"),
                             bg="#FF6B6B",
                             fg="white",
                             padx=20,
                             pady=8,
                             cursor="hand2",
                             command=cancel)
    cancel_button.pack(side="left")
    
    update_button = tk.Button(button_frame,
                             text="Update",
                             font=("Arial", 10, "bold"),
                             bg="#4CAF50",
                             fg="white",
                             padx=20,
                             pady=8,
                             cursor="hand2",
                             command=update_info)
    update_button.pack(side="right")
    
    # Focus on office combo
    office_combo.focus()
    
    # Keyboard support
    def on_key_press(event):
        if event.keysym == 'Return':
            update_info()
        elif event.keysym == 'Escape':
            cancel()
    
    update_window.bind('<Key>', on_key_press)
    
    # Make window modal
    update_window.transient()
    update_window.grab_set()
    update_window.wait_window()
    
    return result[0]

# Add other helper functions (same as before)
def show_error_gui(title, error_message, details=None):
    """Display error message in a GUI window"""
    show_results_gui(
        title=title,
        text=error_message,
        success=False,
        details={"Error Details": details} if details else None
    )

def show_success_gui(title, message, image=None, details=None):
    """Display success message in a GUI window"""
    show_results_gui(
        title=title,
        text=message,
        image=image,
        success=True,
        details=details
    )

def show_message_gui(message, title="MotorPass", message_type="info"):
    """Show a message in a GUI dialog"""
    if message_type.lower() == "error":
        messagebox.showerror(title, message)
    elif message_type.lower() == "warning":
        messagebox.showwarning(title, message)
    elif message_type.lower() == "success":
        messagebox.showinfo(title, f"✅ {message}")
    else:
        messagebox.showinfo(title, message)

def get_user_input_gui(prompt, title="Input Required", default_value=""):
    """
    Thread-safe GUI input dialog with better focus handling
    
    Args:
        prompt (str): The prompt message
        title (str): Dialog title  
        default_value (str): Default input value
        
    Returns:
        str or None: User input or None if cancelled
    """
    result = [None]  # Use list to store result from nested function
    
    def create_dialog():
        # Create dialog window
        dialog = tk.Toplevel()
        dialog.title(title)
        dialog.geometry("500x300")
        dialog.configure(bg="#FFFFFF")
        dialog.resizable(False, False)
        
        # Center the window
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (dialog.winfo_screenheight() // 2) - (300 // 2)
        dialog.geometry(f"500x300+{x}+{y}")
        
        # Make window modal and stay on top
        dialog.transient()
        dialog.grab_set()
        dialog.attributes('-topmost', True)
        dialog.focus_force()  # Force focus
        
        # Main container
        main_frame = tk.Frame(dialog, bg="#FFFFFF", padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)
        
        # Title
        title_label = tk.Label(main_frame,
                              text=title,
                              font=("Arial", 16, "bold"),
                              fg="#2C3E50",
                              bg="#FFFFFF")
        title_label.pack(pady=(0, 15))
        
        # Prompt message
        prompt_label = tk.Label(main_frame,
                               text=prompt,
                               font=("Arial", 12),
                               fg="#34495E",
                               bg="#FFFFFF",
                               wraplength=450,
                               justify="left")
        prompt_label.pack(pady=(0, 20))
        
        # Input frame
        input_frame = tk.Frame(main_frame, bg="#FFFFFF")
        input_frame.pack(fill="x", pady=(0, 20))
        
        input_label = tk.Label(input_frame,
                              text="Enter name:",
                              font=("Arial", 11, "bold"),
                              fg="#34495E",
                              bg="#FFFFFF")
        input_label.pack(anchor="w", pady=(0, 5))
        
        # Text entry
        entry_var = tk.StringVar(value=default_value)
        entry = tk.Entry(input_frame,
                        textvariable=entry_var,
                        font=("Arial", 12),
                        width=40,
                        relief="solid",
                        bd=1)
        entry.pack(fill="x", pady=(0, 10))
        
        # Focus on the entry field and select all text
        entry.focus_set()
        entry.select_range(0, tk.END)
        
        # Buttons frame
        button_frame = tk.Frame(main_frame, bg="#FFFFFF")
        button_frame.pack(fill="x", pady=(10, 0))
        
        def on_ok():
            result[0] = entry_var.get().strip()
            dialog.destroy()
        
        def on_cancel():
            result[0] = None
            dialog.destroy()
        
        # Cancel button
        cancel_btn = tk.Button(button_frame,
                              text="Cancel",
                              font=("Arial", 11),
                              bg="#95A5A6",
                              fg="white",
                              padx=20,
                              pady=8,
                              relief="flat",
                              cursor="hand2",
                              command=on_cancel)
        cancel_btn.pack(side="left")
        
        # OK button
        ok_btn = tk.Button(button_frame,
                          text="OK",
                          font=("Arial", 11, "bold"),
                          bg="#27AE60",
                          fg="white",
                          padx=20,
                          pady=8,
                          relief="flat",
                          cursor="hand2",
                          command=on_ok)
        ok_btn.pack(side="right")
        
        # Bind Enter key to OK
        def on_enter(event):
            on_ok()
        
        entry.bind('<Return>', on_enter)
        dialog.bind('<Return>', on_enter)
        
        # Bind Escape key to Cancel
        def on_escape(event):
            on_cancel()
        
        dialog.bind('<Escape>', on_escape)
        
        # Handle window close
        dialog.protocol("WM_DELETE_WINDOW", on_cancel)
        
        # Wait for dialog to complete
        dialog.wait_window()
    
    # Run dialog in main thread
    if threading.current_thread() is threading.main_thread():
        create_dialog()
    else:
        # If called from another thread, schedule on main thread
        root = tk.Tk()
        root.withdraw()  # Hide the temporary root
        root.after(0, create_dialog)
        root.mainloop()
        root.destroy()
    
    return result[0]
    
def confirm_action_gui(message, title="Confirm Action"):
    """Show a confirmation dialog"""
    return messagebox.askyesno(title, message)
    
# -------------------- STUDENT HELPERS -----------------

def show_student_verification_gui(student_info, verification_data):
    """
    Show student verification results
    
    Args:
        student_info (dict): Student information
        verification_data (dict): Verification results
    """
    message = verification_data.get('gui_message', '')
    success = 'SUCCESSFUL' in verification_data.get('overall_status', '')
    
    details = {}
    if 'checks' in verification_data:
        for check_name, (status, message) in verification_data['checks'].items():
            details[check_name] = f"{'✅' if status else '❌'} {message}"
    
    show_results_gui(
        title="Student Verification Results",
        text=message,
        success=success,
        details=details
    )

def show_guest_verification_gui(guest_info, verification_data):
    """
    Show guest verification results
    
    Args:
        guest_info (dict): Guest information
        verification_data (dict): Verification results
    """
    message = verification_data.get('gui_message', '')
    success = 'SUCCESSFUL' in verification_data.get('overall_status', '')
    
    details = {}
    if 'checks' in verification_data:
        for check_name, (status, message) in verification_data['checks'].items():
            details[check_name] = f"{'✅' if status else '❌'} {message}"
    
    show_results_gui(
        title="Guest Verification Results",
        text=message,
        success=success,
        details=details
    )

def create_loading_dialog(title="Processing...", message="Please wait..."):
    """
    Create a loading dialog window
    
    Args:
        title (str): Dialog title
        message (str): Loading message
        
    Returns:
        tk.Toplevel: The loading window (call destroy() when done)
    """
    loading_window = tk.Toplevel()
    loading_window.title(title)
    loading_window.geometry("300x150")
    loading_window.configure(bg="#FFFFFF")
    
    # Center the window
    loading_window.update_idletasks()
    x = (loading_window.winfo_screenwidth() // 2) - (300 // 2)
    y = (loading_window.winfo_screenheight() // 2) - (150 // 2)
    loading_window.geometry(f"300x150+{x}+{y}")
    
    # Remove window decorations
    loading_window.overrideredirect(True)
    
    # Main frame with border
    main_frame = tk.Frame(loading_window, bg="#FFFFFF", bd=2, relief="raised")
    main_frame.pack(fill="both", expand=True)
    
    # Loading message
    message_label = tk.Label(main_frame,
                           text=message,
                           font=("Arial", 12, "bold"),
                           fg="#333333",
                           bg="#FFFFFF")
    message_label.pack(pady=20)
    
    # Progress bar
    progress = ttk.Progressbar(main_frame, mode='indeterminate', length=200)
    progress.pack(pady=10)
    progress.start()
    
    # Make window stay on top

    loading_window.lift()
    loading_window.attributes('-topmost', True)
    
    return loading_window
    
