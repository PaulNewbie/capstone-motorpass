# etc/ui/vip_gui.py
import tkinter as tk
from tkinter import messagebox
import time 
from datetime import datetime

from etc.controllers.vip import (
    determine_vip_action,
    validate_vip_plate_format
)

from etc.services.hardware.buzzer_control import play_failure
from database.vip_operations import get_all_vip_records

def handle_vip_access(parent_root):
    """Handle VIP access button click with fingerprint authentication GUI"""
    print("\n🌟 VIP ACCESS REQUESTED")
    print("🔐 Admin authentication required for VIP access...")
    
    # CRITICAL: Ensure main window stays visible throughout entire VIP process
    if parent_root:
        parent_root.deiconify()
        parent_root.attributes('-topmost', False)
    
    try:
        from etc.ui.fingerprint_gui import AdminFingerprintGUI
        import threading
        
        print("Using AdminFingerprintGUI for VIP authentication...")
        
        admin_gui = AdminFingerprintGUI(parent_root)
        guard_info = {'name': None, 'slot': None, 'fingerprint_id': None}
        
        def run_auth():
            from etc.services.hardware.fingerprint import finger, adafruit_fingerprint
            from etc.utils.json_database import load_admin_database, load_fingerprint_database
            import time
            
            attempts = 0
            max_attempts = 3 
            
            while attempts < max_attempts:
                attempts += 1
                print(f"VIP Auth attempt {attempts}/{max_attempts}")
                
                admin_gui.root.after(0, lambda: admin_gui.update_status(f"👆 Place admin finger... (Attempt {attempts}/{max_attempts})", "#3498db"))
                
                # Wait for finger
                finger_detected = False
                for _ in range(100):
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
                        play_failure()
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
                            play_failure()
                            admin_gui.root.after(0, admin_gui.show_failed)
                            return
                except:
                    if attempts < max_attempts:
                        admin_gui.root.after(0, lambda: admin_gui.update_status("❌ Processing failed! Try again...", "#e74c3c"))
                        time.sleep(2)
                        continue
                    else:
                        play_failure()
                        admin_gui.root.after(0, admin_gui.show_failed)
                        return
                
                # Search fingerprint
                admin_gui.root.after(0, lambda: admin_gui.update_status("🔍 Searching...", "#3498db"))
                
                try:
                    if finger.finger_search() != adafruit_fingerprint.OK:
                        if attempts < max_attempts:
                            admin_gui.root.after(0, lambda: admin_gui.update_status("❌ Not found! Try again...", "#e74c3c"))
                            time.sleep(2)
                            continue
                        else:
                            play_failure()
                            admin_gui.root.after(0, admin_gui.show_failed)
                            return
                except:
                    if attempts < max_attempts:
                        admin_gui.root.after(0, lambda: admin_gui.update_status("❌ Search failed! Try again...", "#e74c3c"))
                        time.sleep(2)
                        continue
                    else:
                        play_failure()
                        admin_gui.root.after(0, admin_gui.show_failed)
                        return
                
                matched_slot = str(finger.finger_id)
                
                # Capture guard information
                if matched_slot == "1":
                    try:
                        admin_db = load_admin_database()
                        user_name = admin_db.get("1", {}).get("name", "Super Admin")
                    except:
                        user_name = "Super Admin"
                    
                    guard_info['name'] = user_name
                    guard_info['slot'] = matched_slot
                    guard_info['fingerprint_id'] = matched_slot
                    print(f"✅ Super Admin authenticated: {user_name} (Slot 1)")
                    
                elif matched_slot == "2":
                    try:
                        fingerprint_db = load_fingerprint_database()
                        user_name = fingerprint_db.get("2", {}).get("name", "Guard User")
                    except:
                        user_name = "Guard User"
                    
                    guard_info['name'] = user_name
                    guard_info['slot'] = matched_slot
                    guard_info['fingerprint_id'] = matched_slot
                    print(f"✅ Guard authenticated: {user_name} (Slot 2)")
                    
                else:
                    try:
                        fingerprint_db = load_fingerprint_database()
                        
                        if matched_slot not in fingerprint_db:
                            if attempts < max_attempts:
                                admin_gui.root.after(0, lambda: admin_gui.update_status("❌ User not enrolled! Try again...", "#e74c3c"))
                                time.sleep(2)
                                continue
                            else:
                                play_failure()
                                admin_gui.root.after(0, admin_gui.show_failed)
                                return
                        
                        finger_info = fingerprint_db[matched_slot]
                        user_type = finger_info.get('user_type')
                        user_name = finger_info.get('name', 'Unknown')
                        
                        # Only STAFF can access admin panel
                        if user_type != 'STAFF':
                            if attempts < max_attempts:
                                admin_gui.root.after(0, lambda: admin_gui.update_status("❌ Only staff can access admin! Try again...", "#e74c3c"))
                                time.sleep(2)
                                continue
                            else:
                                play_failure()
                                admin_gui.root.after(0, admin_gui.show_failed)
                                return
                        
                        guard_info['name'] = user_name
                        guard_info['slot'] = matched_slot
                        guard_info['fingerprint_id'] = matched_slot
                        print(f"✅ Staff Admin authenticated: {user_name} (Slot {matched_slot})")
                        
                    except Exception as e:
                        print(f"❌ Database error: {e}")
                        if attempts < max_attempts:
                            admin_gui.root.after(0, lambda: admin_gui.update_status("❌ Database error! Try again...", "#e74c3c"))
                            time.sleep(2)
                            continue
                        else:
                            play_failure()
                            admin_gui.root.after(0, admin_gui.show_failed)
                            return
                
                print(f"🎯 Confidence: {finger.confidence}")
                admin_gui.root.after(0, admin_gui.show_success)
                return
            
            # All attempts failed - trigger alarm
            play_failure()
            admin_gui.root.after(0, admin_gui.show_failed)
        
        # Start authentication in thread
        auth_thread = threading.Thread(target=run_auth, daemon=True)
        auth_thread.start()
        
        # Wait for GUI to close
        admin_gui.root.wait_window()
        
        authenticated = admin_gui.auth_result
        
        # Keep main window visible
        if parent_root:
            parent_root.deiconify()
            parent_root.lift()
            parent_root.focus_set()
        
        if not authenticated:
            print("❌ VIP access denied - authentication failed")
            return
            
        print("✅ Authentication successful - Opening VIP access panel")
        
    except Exception as e:
        print(f"❌ VIP authentication error: {e}")
        return
        
    # Open VIP window with guard info
    open_vip_window(parent_root, guard_info)


def open_vip_window(parent_root=None, guard_info=None):
    """Open VIP window with quick select buttons for currently inside visitors"""
    
    vip_window = tk.Toplevel(parent_root)
    vip_window.title("VIP Access Panel")
    vip_window.geometry("600x800")
    vip_window.configure(bg="white")
    vip_window.resizable(False, False)
    
    # IMPORTANT: Final check to ensure main window stays visible
    if parent_root:
        parent_root.deiconify()
        parent_root.attributes('-topmost', False)
        parent_root.update()
    
    # Center VIP window
    vip_window.update_idletasks()
    screen_width = vip_window.winfo_screenwidth()
    screen_height = vip_window.winfo_screenheight()
    x = (screen_width // 2) - (300)
    y = (screen_height // 2) - (400)
    vip_window.geometry(f"600x800+{x}+{y}")
    
    # Handle VIP window close event
    def on_vip_window_close():
        if parent_root:
            parent_root.deiconify()
            parent_root.lift()
            parent_root.focus_set()
        vip_window.destroy()
    
    vip_window.protocol("WM_DELETE_WINDOW", on_vip_window_close)
    
    # Create the complete VIP form
    try:
        # === HEADER ===
        print("🔍 DEBUG: Creating header frame...")
        header_frame = tk.Frame(vip_window, bg="#FF4444", height=80)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="VIP ACCESS", 
                font=("Arial", 20, "bold"), fg="white", bg="#FF4444").pack(expand=True)
        print("🔍 DEBUG: Header created")
        
        # === SCROLLABLE MAIN CONTAINER ===
        main_container = tk.Frame(vip_window, bg="white")
        main_container.pack(fill="both", expand=True)
        
        canvas = tk.Canvas(main_container, bg="white", highlightthickness=0)
        scrollbar = tk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="white")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Make scrollable frame fill canvas width
        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            # Make the frame width match canvas width
            canvas.itemconfig(canvas_window, width=event.width)
        
        canvas.bind('<Configure>', configure_scroll_region)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Mousewheel scrolling
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        # === MANUAL ENTRY FORM ===
        print("🔍 DEBUG: Creating form frame...")
        form_frame = tk.Frame(scrollable_frame, bg="white")
        form_frame.pack(fill="x", padx=30, pady=(20, 10))
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
        status_label.pack(pady=(0, 10))
        print("🔍 DEBUG: Status label created")
        
        # Purpose selection frame (hidden initially) - MULTIPLE CHOICE
        purpose_frame = tk.Frame(form_frame, bg="white")
        purpose_vars = {}
        purpose_checkboxes = []
        
        tk.Label(purpose_frame, text="Select Purpose(s):", 
                font=("Arial", 11, "bold"), bg="white", fg="#34495E").pack(anchor="w", pady=(0,10))
        
        # Create checkboxes grid
        checkboxes_grid_frame = tk.Frame(purpose_frame, bg="white")
        checkboxes_grid_frame.pack(fill="x")
        
        purposes = ["Official Visit", "Meeting", "Inspection", "Emergency", "Other"]
        for i, purpose in enumerate(purposes):
            purpose_vars[purpose] = tk.BooleanVar()
            
            checkbox = tk.Checkbutton(checkboxes_grid_frame, 
                                    text=purpose, 
                                    font=("Arial", 10),
                                    variable=purpose_vars[purpose],
                                    bg="white", 
                                    fg="black",
                                    selectcolor="#27AE60",
                                    cursor="hand2")
            checkbox.grid(row=i//2, column=i%2, padx=10, pady=3, sticky="w")
            purpose_checkboxes.append(checkbox)
        
        # Configure grid weights
        for i in range(2):
            checkboxes_grid_frame.grid_columnconfigure(i, weight=1)
        
        other_purpose_frame = tk.Frame(purpose_frame, bg="white")
        tk.Label(other_purpose_frame, text="Specify Other Purpose:", 
                font=("Arial", 10), bg="white", fg="#34495E").pack(anchor="w", pady=(5,3))
        other_purpose_entry = tk.Entry(other_purpose_frame, font=("Arial", 10), width=30)
        other_purpose_entry.pack(anchor="w")
        
        # Function to show/hide "Other" input box
        def toggle_other_input():
            if purpose_vars["Other"].get():
                other_purpose_frame.pack(fill="x", pady=(5,0))
                other_purpose_entry.focus_set()
            else:
                other_purpose_frame.pack_forget()
                other_purpose_entry.delete(0, tk.END)
        
        # Bind "Other" checkbox to toggle function
        purpose_vars["Other"].trace_add("write", lambda *args: toggle_other_input())
        
        
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
                status_label.config(text="TIME IN - Select purpose(s) below", fg="#27AE60")
                purpose_frame.pack(fill="x", pady=10)
                # Reset all checkboxes
                for purpose_var in purpose_vars.values():
                    purpose_var.set(False)
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
        button_frame.pack(pady=(20,0)) 
        
        def cancel_vip():
            if parent_root:
                parent_root.deiconify()
                parent_root.lift()
                parent_root.focus_set()
            vip_window.destroy()
        
        def submit_vip():
            plate_number = plate_entry.get().strip().upper()

            if not plate_number:
                status_label.config(text="⚠️ Please enter plate number!", fg="#E74C3C")
                return

            # Run validation
            is_valid, validation_msg = validate_vip_plate_format(plate_number)
            if not is_valid:
                status_label.config(text=f"❌ {validation_msg}", fg="#E74C3C")
                return

            # Determine action (TIME IN / TIME OUT)
            action_result = determine_vip_action(plate_number)
            
            # Check if it's a special plate for display
            special_info = None
            if validation_msg.startswith("Special Plate:"):
                special_info = validation_msg

            if action_result['action'] == 'TIME_IN':
                selected_purposes = []
                for purpose, var in purpose_vars.items():
                    if var.get():
                        # If "Other" is selected, use the custom text from input box
                        if purpose == "Other":
                            custom_purpose = other_purpose_entry.get().strip()
                            if custom_purpose:
                                selected_purposes.append(custom_purpose)
                            else:
                                status_label.config(text="⚠️ Please specify 'Other' purpose in the text box!", fg="#E67E22")
                                return
                        else:
                            selected_purposes.append(purpose)

                if not selected_purposes:
                    status_label.config(text="⚠️ Please select at least one purpose for TIME IN!", fg="#E67E22")
                    return

                purpose_text = ", ".join(selected_purposes)
                result = process_vip_time_in_with_guard(plate_number, purpose_text, guard_info)

                if result['success']:
                    if special_info:
                        status_label.config(
                            text=f"💎 {special_info}\n✅ TIME IN Successful!\nPlate: {plate_number}\nPurpose: {purpose_text}\nGuard: {guard_info['name']}",
                            fg="#9B59B6"
                        )
                    else:
                        status_label.config(
                            text=f"✅ TIME IN Successful!\nPlate: {plate_number}\nPurpose: {purpose_text}\nGuard: {guard_info['name']}",
                            fg="#27AE60"
                        )
                    plate_entry.delete(0, tk.END)
                    purpose_frame.pack_forget()
                    load_inside_visitors()
                else:
                    status_label.config(text=f"❌ TIME IN failed: {result['message']}", fg="#E74C3C")

            elif action_result['action'] == 'TIME_OUT':
                result = process_vip_time_out_with_guard(plate_number, guard_info)
                if result['success']:
                    vip_info = action_result['vip_info']
                    if special_info:
                        status_label.config(
                            text=f"💎 {special_info}\n✅ TIME OUT Successful!\nPlate: {plate_number}\nPurpose: {vip_info['purpose']}\nGuard: {guard_info['name']}",
                            fg="#9B59B6"
                        )
                    else:
                        status_label.config(
                            text=f"✅ TIME OUT Successful!\nPlate: {plate_number}\nPurpose: {vip_info['purpose']}\nGuard: {guard_info['name']}",
                            fg="#2980B9"
                        )
                    plate_entry.delete(0, tk.END)
                    purpose_frame.pack_forget()
                    load_inside_visitors()
                else:
                    status_label.config(text=f"❌ TIME OUT failed: {result['message']}", fg="#E74C3C")

            else:
                status_label.config(text=f"⚠️ {action_result['message']}", fg="#E74C3C")
        
        # Cancel and Submit buttons
        tk.Button(button_frame, text="Cancel", font=("Arial", 11, "bold"),
                 bg="#95a5a6", fg="white", cursor="hand2",
                 command=cancel_vip, width=12, pady=8).pack(side="left", padx=(0,10))
        
        tk.Button(button_frame, text="Submit", font=("Arial", 11, "bold"),
                 bg="#27AE60", fg="white", cursor="hand2",
                 command=submit_vip, width=12, pady=8).pack(side="right")
        
        # === SEPARATOR ===
        separator = tk.Frame(scrollable_frame, bg="#CCCCCC", height=2)
        separator.pack(fill="x", padx=30, pady=20)
        
        # === CURRENTLY INSIDE SECTION ===
        inside_section = tk.Frame(scrollable_frame, bg="white")
        inside_section.pack(fill="both", expand=True, padx=30, pady=(0, 20))
        
        header_container = tk.Frame(inside_section, bg="white")
        header_container.pack(fill="x", pady=(0, 15))
        
        tk.Label(header_container, text="Currently Inside Visitors", 
                font=("Arial", 14, "bold"), fg="#2C3E50", bg="white").pack(side="left")
        
        def manual_refresh():
            load_inside_visitors()
        
        tk.Button(header_container, text="🔄 Refresh", command=manual_refresh,
                 font=("Arial", 9), bg="#ECF0F1", fg="#2C3E50",
                 relief="flat", padx=10, pady=5, cursor="hand2").pack(side="right")
        
        vip_buttons_container = tk.Frame(inside_section, bg="white")
        vip_buttons_container.pack(fill="both", expand=True)
        
        def load_inside_visitors():
            """Load and display currently inside VIP visitors"""
            for widget in vip_buttons_container.winfo_children():
                widget.destroy()
            
            current_vips = get_all_vip_records(status='IN')
            
            if not current_vips:
                tk.Label(vip_buttons_container, 
                        text="No VIP visitors currently inside", 
                        font=("Arial", 11), fg="#95A5A6", bg="white",
                        pady=20).pack()
            else:
                for vip_record in current_vips:
                    create_visitor_button(vip_record)
        
        def create_visitor_button(vip_record):
            """Create a button for each VIP visitor"""
            plate_number = vip_record[1]
            purpose = vip_record[2]
            time_in = vip_record[3]
            
            try:
                time_obj = datetime.fromisoformat(time_in)
                time_display = time_obj.strftime("%I:%M %p")
            except:
                time_display = str(time_in)[:5] if len(str(time_in)) > 5 else str(time_in)
            
            # FIXED: Set explicit background colors from the start
            btn_frame = tk.Frame(vip_buttons_container, bg="#F8F9FA", relief="solid", 
                                bd=1, highlightbackground="#BDC3C7", highlightthickness=1)
            btn_frame.pack(fill="x", pady=5, ipady=5)
            
            content_frame = tk.Frame(btn_frame, bg="#F8F9FA")
            content_frame.pack(fill="x", padx=10, pady=5)
            
            tk.Label(content_frame, text=plate_number, 
                    font=("Arial", 16, "bold"), fg="#2C3E50", bg="#F8F9FA").pack(side="left")
            
            info_frame = tk.Frame(content_frame, bg="#F8F9FA")
            info_frame.pack(side="left", fill="x", expand=True, padx=20)
            
            tk.Label(info_frame, text=f"Purpose: {purpose}", 
                    font=("Arial", 9), fg="#7F8C8D", bg="#F8F9FA").pack(anchor="w")
            tk.Label(info_frame, text=f"Time In: {time_display}", 
                    font=("Arial", 9), fg="#95A5A6", bg="#F8F9FA").pack(anchor="w")
            
            def quick_select():
                """Fill plate number in entry box"""
                plate_entry.delete(0, tk.END)
                plate_entry.insert(0, plate_number)
                check_plate_status()
                canvas.yview_moveto(0)
            
            select_btn = tk.Button(content_frame, text="SELECT", 
                                   command=quick_select,
                                   font=("Arial", 10, "bold"), bg="#3498DB", fg="white",
                                   relief="flat", padx=15, pady=8, cursor="hand2")
            select_btn.pack(side="right")
            
            # Hover effects - change to slightly darker color
            def on_enter(e):
                btn_frame.config(bg="#E9ECEF")
                content_frame.config(bg="#E9ECEF")
                info_frame.config(bg="#E9ECEF")
                for child in info_frame.winfo_children():
                    child.config(bg="#E9ECEF")
                for child in content_frame.winfo_children():
                    if isinstance(child, tk.Label):
                        child.config(bg="#E9ECEF")
            
            def on_leave(e):
                btn_frame.config(bg="#F8F9FA")
                content_frame.config(bg="#F8F9FA")
                info_frame.config(bg="#F8F9FA")
                for child in info_frame.winfo_children():
                    child.config(bg="#F8F9FA")
                for child in content_frame.winfo_children():
                    if isinstance(child, tk.Label):
                        child.config(bg="#F8F9FA")
            
            btn_frame.bind("<Enter>", on_enter)
            btn_frame.bind("<Leave>", on_leave)
            content_frame.bind("<Enter>", on_enter)
            content_frame.bind("<Leave>", on_leave)
        
        # Initial load of visitors
        load_inside_visitors()
        
        print("🔍 DEBUG: All VIP window components created successfully!")
        print("🔍 DEBUG: VIP window should now be fully visible and functional!")
        
    except Exception as content_error:
        print(f"❌ Error creating VIP window content: {content_error}")
        if 'vip_window' in locals():
            vip_window.destroy()
        
        # Ensure main window is still visible on error
        if parent_root:
            parent_root.deiconify()
            parent_root.lift()


# Helper functions
def process_vip_time_in_with_guard(plate_number, purpose, guard_info):
    """Process VIP TIME IN with guard information"""
    try:
        from etc.controllers.vip import process_vip_time_in_with_guard as controller_func
        return controller_func(plate_number, purpose, guard_info)
    except ImportError:
        from etc.controllers.vip import process_vip_time_in
        return process_vip_time_in(plate_number, purpose)


def process_vip_time_out_with_guard(plate_number, guard_info):
    """Process VIP TIME OUT with guard information"""
    try:
        from etc.controllers.vip import process_vip_time_out_with_guard as controller_func
        return controller_func(plate_number, guard_info)
    except ImportError:
        from etc.controllers.vip import process_vip_time_out
        return process_vip_time_out(plate_number)
