# etc/ui/vip_gui.py
import tkinter as tk
from tkinter import messagebox

from etc.controllers.vip import (
    determine_vip_action,
    process_vip_time_in,
    process_vip_time_out,
    validate_vip_plate_format
)

def handle_vip_access(parent_root):
    """Handle VIP access button click with fingerprint authentication GUI"""
    print("\n🌟 VIP ACCESS REQUESTED")
    print("🔐 Admin authentication required for VIP access...")
    
    # CRITICAL: Ensure main window stays visible throughout entire VIP process
    if parent_root:
        parent_root.deiconify()           # Make sure main window is visible
        parent_root.attributes('-topmost', False)  # Don't force on top
    
    # Import and use the AdminFingerprintGUI (same as Admin button uses)
    try:
        from etc.ui.fingerprint_gui import AdminFingerprintGUI
        import threading
        
        print("Using AdminFingerprintGUI for VIP authentication...")
        
        # Create the fingerprint GUI (will keep main window visible as background)
        admin_gui = AdminFingerprintGUI(parent_root)
        
        def run_auth():
            # This runs the same authentication logic as Admin button
            from etc.services.hardware.fingerprint import finger, adafruit_fingerprint
            import time
            
            attempts = 0
            max_attempts = 3
            
            while attempts < max_attempts:
                attempts += 1
                print(f"VIP Auth attempt {attempts}/{max_attempts}")
                
                # Update GUI
                admin_gui.root.after(0, lambda: admin_gui.update_status(f"👆 Place admin finger... (Attempt {attempts}/{max_attempts})", "#3498db"))
                
                # Wait for finger and process
                finger_detected = False
                for _ in range(100):  # 10 second timeout
                    try:
                        if finger.get_image() == adafruit_fingerprint.OK:
                            finger_detected = True
                            break
                    except:
                        pass
                    time.sleep(0.1)
                
                if not finger_detected:
                    if attempts < max_attempts:
                        admin_gui.root.after(0, lambda: admin_gui.update_status("⏰ Timeout! Try again...", "#e67e22"))
                        time.sleep(2)
                        continue
                    else:
                        admin_gui.root.after(0, admin_gui.show_failed)
                        return
                
                # Process fingerprint
                admin_gui.root.after(0, lambda: admin_gui.update_status("🔄 Processing...", "#f39c12"))
                
                try:
                    if finger.image_2_tz(1) != adafruit_fingerprint.OK:
                        if attempts < max_attempts:
                            admin_gui.root.after(0, lambda: admin_gui.update_status("❌ Processing failed! Try again...", "#e74c3c"))
                            time.sleep(2)
                            continue
                        else:
                            admin_gui.root.after(0, admin_gui.show_failed)
                            return
                except:
                    if attempts < max_attempts:
                        admin_gui.root.after(0, lambda: admin_gui.update_status("❌ Sensor error! Try again...", "#e74c3c"))
                        time.sleep(2)
                        continue
                    else:
                        admin_gui.root.after(0, admin_gui.show_failed)
                        return
                
                # Search for fingerprint
                admin_gui.root.after(0, lambda: admin_gui.update_status("🔍 Searching...", "#9b59b6"))
                
                try:
                    if finger.finger_search() != adafruit_fingerprint.OK:
                        if attempts < max_attempts:
                            admin_gui.root.after(0, lambda: admin_gui.update_status("❌ No match found! Try again...", "#e74c3c"))
                            time.sleep(2)
                            continue
                        else:
                            admin_gui.root.after(0, admin_gui.show_failed)
                            return
                    
                    # Check if matched fingerprint is admin (slot 1)
                    if finger.finger_id == 1:
                        admin_gui.root.after(0, admin_gui.show_success)
                        return
                    else:
                        if attempts < max_attempts:
                            admin_gui.root.after(0, lambda: admin_gui.update_status("❌ Not admin fingerprint! Try again...", "#e74c3c"))
                            time.sleep(2)
                            continue
                        else:
                            admin_gui.root.after(0, admin_gui.show_failed)
                            return
                            
                except:
                    if attempts < max_attempts:
                        admin_gui.root.after(0, lambda: admin_gui.update_status("❌ Search failed! Try again...", "#e74c3c"))
                        time.sleep(2)
                        continue
                    else:
                        admin_gui.root.after(0, admin_gui.show_failed)
                        return
            
            # All attempts failed
            admin_gui.root.after(0, admin_gui.show_failed)
        
        # Start authentication in thread
        auth_thread = threading.Thread(target=run_auth, daemon=True)
        auth_thread.start()
        
        # Wait for GUI to close
        admin_gui.root.wait_window()
        
        # Use the AdminFingerprintGUI's auth_result
        authenticated = admin_gui.auth_result
        
        # CRITICAL: Ensure main window is still visible after authentication
        if parent_root:
            parent_root.deiconify()
            parent_root.lift()
            parent_root.focus_set()
        
        if not authenticated:
            print("❌ VIP access denied - authentication failed")
            return
            
        print("✅ Authentication successful - Opening VIP access panel")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        messagebox.showerror("Error", f"Could not import GUI authentication: {str(e)}")
        return
    except Exception as e:
        print(f"❌ VIP authentication error: {e}")
        messagebox.showerror("Error", f"Authentication failed: {str(e)}")
        return
        
    # Create VIP window with main window staying visible as background
    vip_window = tk.Toplevel(parent_root)
    vip_window.title("VIP Access Panel")
    vip_window.geometry("500x600")
    vip_window.configure(bg="white")
    vip_window.resizable(False, False)
    
    # IMPORTANT: Final check to ensure main window stays visible
    if parent_root:
        parent_root.deiconify()           # Keep main window visible
        parent_root.attributes('-topmost', False)  # Allow normal window behavior
        parent_root.update()              # Force update
    
    # Center VIP window
    vip_window.update_idletasks()
    screen_width = vip_window.winfo_screenwidth()
    screen_height = vip_window.winfo_screenheight()
    x = (screen_width // 2) - (500 // 2)
    y = (screen_height // 2) - (600 // 2)
    vip_window.geometry(f"500x600+{x}+{y}")
    
    # Handle VIP window close event to ensure main window stays visible
    def on_vip_window_close():
        """Ensure main window stays visible when VIP window is closed"""
        if parent_root:
            parent_root.deiconify()
            parent_root.lift()
            parent_root.focus_set()
        vip_window.destroy()
    
    vip_window.protocol("WM_DELETE_WINDOW", on_vip_window_close)
    
    # Create the complete VIP form
    try:
        # Header
        print("🔍 DEBUG: Creating header frame...")
        header_frame = tk.Frame(vip_window, bg="#FF4444", height=80)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="VIP ACCESS", 
                font=("Arial", 20, "bold"), fg="white", bg="#FF4444").pack(expand=True)
        print("🔍 DEBUG: Header created")
        
        # Main form frame
        print("🔍 DEBUG: Creating form frame...")
        form_frame = tk.Frame(vip_window, bg="white")
        form_frame.pack(fill="both", expand=True, padx=30, pady=30)
        print("🔍 DEBUG: Form frame created")
        
        # Instructions
        instructions = tk.Label(form_frame, 
                               text="Enter plate number - System will automatically\ndetermine TIME IN or TIME OUT",
                               font=("Arial", 11), 
                               fg="#666666", bg="white",
                               justify="center")
        instructions.pack(pady=(0, 20))
        print("🔍 DEBUG: Instructions added")
        
        # Plate Number Input
        tk.Label(form_frame, text="Plate Number:", 
                font=("Arial", 12, "bold"), bg="white", fg="#34495E").pack(anchor="w", pady=(0,5))
        
        plate_entry = tk.Entry(form_frame, font=("Arial", 14), 
                              width=25, justify="center")
        plate_entry.pack(pady=(0, 10), fill="x")
        plate_entry.focus_set()
        print("🔍 DEBUG: Plate entry created")
        
        # Status display
        status_label = tk.Label(form_frame, text="Enter plate number to check status", 
                               font=("Arial", 11), fg="#7F8C8D", bg="white",
                               wraplength=350, justify="center")
        status_label.pack(pady=(0, 20))
        print("🔍 DEBUG: Status label created")
        
        # Purpose selection frame (hidden initially)
        purpose_frame = tk.Frame(form_frame, bg="white")
        purpose_var = tk.StringVar()
        purpose_buttons = []
        
        tk.Label(purpose_frame, text="Select Purpose:", 
                font=("Arial", 11, "bold"), bg="white", fg="#34495E").pack(anchor="w", pady=(0,10))
        
        # Create a sub-frame for the button grid to avoid geometry manager conflict
        buttons_grid_frame = tk.Frame(purpose_frame, bg="white")
        buttons_grid_frame.pack(fill="x")
        
        purposes = ["Meeting", "Delivery", "Maintenance", "Inspection", "Other"]
        for i, purpose in enumerate(purposes):
            btn = tk.Button(buttons_grid_frame, text=purpose, font=("Arial", 9),
                           bg="#f0f0f0", fg="black", bd=1, relief='solid',
                           width=12, cursor="hand2")
            btn.grid(row=i//3, column=i%3, padx=3, pady=3, sticky="ew")
            purpose_buttons.append(btn)
            
            def select_purpose(p=purpose, b=btn):
                purpose_var.set(p)
                for button in purpose_buttons:
                    button.config(bg="#f0f0f0", fg="black")
                b.config(bg="#27AE60", fg="white")
            
            btn.config(command=select_purpose)
        
        # Configure grid weights for the buttons_grid_frame
        for i in range(3):
            buttons_grid_frame.grid_columnconfigure(i, weight=1)
        
        print("🔍 DEBUG: Purpose buttons created")
        
        def check_plate_status():
            plate_number = plate_entry.get().strip().upper()
            if not plate_number:
                status_label.config(text="Enter plate number to check status", fg="#7F8C8D")
                purpose_frame.pack_forget()
                return
            
            # Validate plate format
            is_valid, validation_msg = validate_vip_plate_format(plate_number)
            if not is_valid:
                status_label.config(text=f"Invalid: {validation_msg}", fg="#E74C3C")
                purpose_frame.pack_forget()
                return
            
            # Determine action
            action_result = determine_vip_action(plate_number)
            
            if action_result['action'] == 'TIME_IN':
                status_label.config(text="TIME IN - Select purpose below", fg="#27AE60")
                purpose_frame.pack(fill="x", pady=10)
                purpose_var.set("")  # Reset purpose
                # Reset button colors
                for btn in purpose_buttons:
                    btn.config(bg="#f0f0f0", fg="black")
            elif action_result['action'] == 'TIME_OUT':
                vip_info = action_result['vip_info']
                status_label.config(text=f"TIME OUT - {vip_info['purpose']}", fg="#E74C3C")
                purpose_frame.pack_forget()
            else:
                status_label.config(text=f"Error: {action_result['message']}", fg="#E74C3C")
                purpose_frame.pack_forget()
        
        # Bind plate entry to check status
        plate_entry.bind('<KeyRelease>', lambda e: check_plate_status())
        
        # Buttons frame
        button_frame = tk.Frame(form_frame, bg="white")
        button_frame.pack(side="bottom", fill="x", pady=(30,0))
        
        def cancel_vip():
            # Ensure main window stays visible when cancelled
            if parent_root:
                parent_root.deiconify()
                parent_root.lift()
                parent_root.focus_set()
            vip_window.destroy()
        
        def submit_vip():
            plate_number = plate_entry.get().strip().upper()
            
            if not plate_number:
                messagebox.showerror("Error", "Please enter plate number!")
                return
            
            # Validate plate format
            is_valid, validation_msg = validate_vip_plate_format(plate_number)
            if not is_valid:
                messagebox.showerror("Invalid Plate", validation_msg)
                return
            
            # Determine action
            action_result = determine_vip_action(plate_number)
            
            if action_result['action'] == 'TIME_IN':
                purpose = purpose_var.get()
                if not purpose:
                    messagebox.showerror("Error", "Please select purpose for TIME IN!")
                    return
                
                # Process TIME IN
                result = process_vip_time_in(plate_number, purpose)
                if result['success']:
                    messagebox.showinfo("Success", f"VIP TIME IN successful!\nPlate: {plate_number}\nPurpose: {purpose}")
                    # Ensure main window stays visible after success
                    if parent_root:
                        parent_root.deiconify()
                        parent_root.lift()
                        parent_root.focus_set()
                    vip_window.destroy()
                else:
                    messagebox.showerror("Error", f"TIME IN failed: {result['message']}")
                    
            elif action_result['action'] == 'TIME_OUT':
                # Process TIME OUT
                result = process_vip_time_out(plate_number)
                if result['success']:
                    vip_info = action_result['vip_info']
                    messagebox.showinfo("Success", f"VIP TIME OUT successful!\nPlate: {plate_number}\nPurpose: {vip_info['purpose']}")
                    # Ensure main window stays visible after success
                    if parent_root:
                        parent_root.deiconify()
                        parent_root.lift()
                        parent_root.focus_set()
                    vip_window.destroy()
                else:
                    messagebox.showerror("Error", f"TIME OUT failed: {result['message']}")
            else:
                messagebox.showerror("Error", f"{action_result['message']}")
        
        # Cancel and Submit buttons
        tk.Button(button_frame, text="Cancel", font=("Arial", 11, "bold"),
                 bg="#95a5a6", fg="white", cursor="hand2",
                 command=cancel_vip, width=12, pady=8).pack(side="left", padx=(0,10))
        
        tk.Button(button_frame, text="Submit", font=("Arial", 11, "bold"),
                 bg="#27AE60", fg="white", cursor="hand2",
                 command=submit_vip, width=12, pady=8).pack(side="right")
        
        print("🔍 DEBUG: All VIP window components created successfully!")
        print("🔍 DEBUG: VIP window should now be fully visible and functional!")
        
    except Exception as content_error:
        print(f"❌ Error creating VIP window content: {content_error}")
        messagebox.showerror("Error", f"Failed to create VIP window content: {str(content_error)}")
        if 'vip_window' in locals():
            vip_window.destroy()
        
        # Ensure main window is still visible on error
        if parent_root:
            parent_root.deiconify()
            parent_root.lift()
