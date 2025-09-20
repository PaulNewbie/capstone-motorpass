# etc/ui/dialog_helpers_gui.py - Manual input dialog helpers

import tkinter as tk
from tkinter import messagebox
import queue
import threading

def get_manual_name_input(expected_name, actual_license_name, status_callback, attempt_number=1):
    """Thread-safe manual name input dialog with attempt tracking"""
    dialog_result = queue.Queue()
    
    # Execute in main thread using the GUI's root window
    if hasattr(status_callback, '__self__') and hasattr(status_callback.__self__, 'root'):
        # Use the existing GUI root
        gui_root = status_callback.__self__.root
        gui_root.after(0, lambda: show_manual_input_dialog(expected_name, actual_license_name, dialog_result, attempt_number))
    else:
        # Fallback: create temporary root
        temp_root = tk.Tk()
        temp_root.withdraw()
        temp_root.after(0, lambda: show_manual_input_dialog(expected_name, actual_license_name, dialog_result, attempt_number))
    
    # Wait for result
    try:
        manual_name = dialog_result.get(timeout=60)  # 1 minute timeout
        return manual_name
    except queue.Empty:
        print(f"⏰ Manual input dialog timeout after 60 seconds (attempt {attempt_number})")
        return None

def show_manual_input_dialog(expected_name, actual_license_name, dialog_result_queue, attempt_number=1):
    """Create a professional manual input dialog with attempt tracking"""
    try:
        # Create new toplevel window
        dialog = tk.Toplevel()
        
        # Update title based on attempt number
        if attempt_number == 1:
            dialog.title("Manual Name Override Required - Attempt 1/2")
        else:
            dialog.title("Manual Name Override Required - Last Chance (2/2)")
            
        dialog.geometry("500x350")
        dialog.configure(bg="#FFFFFF")
        dialog.resizable(False, False)
        
        # Center window
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (250)
        y = (dialog.winfo_screenheight() // 2) - (175)
        dialog.geometry(f"500x350+{x}+{y}")
        
        # Make modal and topmost
        dialog.transient()
        dialog.grab_set()
        dialog.attributes('-topmost', True)
        dialog.focus_force()
        
        try:
            from refresh import add_refresh_to_window
            if add_refresh_to_window:
                add_refresh_to_window(dialog)
        except ImportError:
            add_refresh_to_window = None
        
        # Create content
        main_frame = tk.Frame(dialog, bg="#FFFFFF", padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)
        
        # Title with attempt information
        if attempt_number == 1:
            title_text = "⚠️ Manual Override Required (1/2)"
            title_color = "#E74C3C"
        else:
            title_text = "🚨 Last Chance Manual Override (2/2)"
            title_color = "#C0392B"
            
        title_label = tk.Label(main_frame,
                              text=title_text,
                              font=("Arial", 16, "bold"),
                              fg=title_color,
                              bg="#FFFFFF")
        title_label.pack(pady=(0, 15))
        
        # Expected name
        expected_frame = tk.Frame(main_frame, bg="#FFFFFF")
        expected_frame.pack(fill="x", pady=(0, 10))
        
        tk.Label(expected_frame,
                text="Expected Name:",
                font=("Arial", 11, "bold"),
                fg="#2C3E50",
                bg="#FFFFFF").pack(anchor="w")
                
        tk.Label(expected_frame,
                text=expected_name,
                font=("Arial", 12),
                fg="#27AE60",
                bg="#FFFFFF").pack(anchor="w", padx=(20, 0))
        
        # Detected name
        detected_frame = tk.Frame(main_frame, bg="#FFFFFF")
        detected_frame.pack(fill="x", pady=(0, 15))
        
        tk.Label(detected_frame,
                text="Detected on License:",
                font=("Arial", 11, "bold"),
                fg="#2C3E50",
                bg="#FFFFFF").pack(anchor="w")
                
        detected_color = "#E67E22" if actual_license_name and "error" not in actual_license_name.lower() else "#E74C3C"
        tk.Label(detected_frame,
                text=actual_license_name or "Not detected",
                font=("Arial", 12),
                fg=detected_color,
                bg="#FFFFFF").pack(anchor="w", padx=(20, 0))
        
        # Instructions
        instruction_text = (
            "Enter the exact name as it appears on the license:"
            if attempt_number == 1 
            else "FINAL ATTEMPT - Enter the exact name as it appears on the license:"
        )
        
        tk.Label(main_frame,
                text=instruction_text,
                font=("Arial", 11, "bold"),
                fg="#2C3E50",
                bg="#FFFFFF").pack(anchor="w", pady=(0, 5))
        
        # Entry field
        entry_var = tk.StringVar(value=actual_license_name if actual_license_name and "error" not in actual_license_name.lower() else "")
        entry = tk.Entry(main_frame,
                       textvariable=entry_var,
                       font=("Arial", 12),
                       width=50,
                       relief="solid",
                       bd=1)
        entry.pack(fill="x", pady=(0, 20))
        entry.focus_set()
        entry.select_range(0, tk.END)
        
        # Button frame
        button_frame = tk.Frame(main_frame, bg="#FFFFFF")
        button_frame.pack(fill="x")
        
        def on_cancel():
            print(f"   🚫 User cancelled manual input dialog (attempt {attempt_number})")
            dialog_result_queue.put(None)
            dialog.destroy()
        
        def on_ok():
            result = entry_var.get().strip()
            print(f"   📝 User submitted: '{result}' (attempt {attempt_number})")
            dialog_result_queue.put(result)
            dialog.destroy()
        
        # Buttons
        cancel_btn = tk.Button(button_frame,
                             text="Cancel",
                             font=("Arial", 11),
                             bg="#95A5A6",
                             fg="white",
                             padx=25,
                             pady=10,
                             relief="flat",
                             command=on_cancel)
        cancel_btn.pack(side="left")
        
        button_text = "Override & Continue" if attempt_number == 1 else "Final Override"
        ok_btn = tk.Button(button_frame,
                          text=button_text,
                          font=("Arial", 11, "bold"),
                          bg="#27AE60",
                          fg="white",
                          padx=25,
                          pady=10,
                          relief="flat",
                          command=on_ok)
        ok_btn.pack(side="right")
        
        # Key bindings
        entry.bind('<Return>', lambda e: on_ok())
        dialog.bind('<Escape>', lambda e: on_cancel())
        dialog.protocol("WM_DELETE_WINDOW", on_cancel)
        
        # Wait for dialog
        dialog.wait_window()
        
    except Exception as e:
        print(f"Dialog creation error (attempt {attempt_number}): {e}")
        dialog_result_queue.put(None)
