# etc/ui/dialog_helpers_gui.py - Manual input dialog helpers

import tkinter as tk
from tkinter import messagebox
import queue
import threading

def show_manual_input_dialog(expected_name, actual_license_name, dialog_result_queue):
    """Create a professional manual input dialog"""
    try:
        # Create new toplevel window
        dialog = tk.Toplevel()
        dialog.title("Manual Name Override Required")
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
        
        # Create content
        main_frame = tk.Frame(dialog, bg="#FFFFFF", padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)
        
        # Title
        title_label = tk.Label(main_frame,
                              text="⚠️ Manual Override Required",
                              font=("Arial", 16, "bold"),
                              fg="#E74C3C",
                              bg="#FFFFFF")
        title_label.pack(pady=(0, 15))
        
        # Info frame
        info_frame = tk.LabelFrame(main_frame, 
                                  text=" Verification Details ",
                                  font=("Arial", 11, "bold"),
                                  fg="#2C3E50",
                                  bg="#FFFFFF")
        info_frame.pack(fill="x", pady=(0, 20))
        
        # Expected name
        expected_frame = tk.Frame(info_frame, bg="#FFFFFF")
        expected_frame.pack(fill="x", padx=10, pady=5)
        tk.Label(expected_frame, text="Expected Name:", 
                font=("Arial", 10, "bold"), fg="#34495E", 
                bg="#FFFFFF").pack(anchor="w")
        tk.Label(expected_frame, text=expected_name,
                font=("Arial", 10), fg="#27AE60", 
                bg="#FFFFFF").pack(anchor="w", padx=(10, 0))
        
        # Detected name
        detected_frame = tk.Frame(info_frame, bg="#FFFFFF")
        detected_frame.pack(fill="x", padx=10, pady=5)
        tk.Label(detected_frame, text="License Shows:", 
                font=("Arial", 10, "bold"), fg="#34495E", 
                bg="#FFFFFF").pack(anchor="w")
        tk.Label(detected_frame, text=actual_license_name if actual_license_name else 'Not clearly detected',
                font=("Arial", 10), fg="#E74C3C", 
                bg="#FFFFFF").pack(anchor="w", padx=(10, 0))
        
        # Input section
        input_label = tk.Label(main_frame,
                              text="Enter the correct name shown on the license:",
                              font=("Arial", 11, "bold"),
                              fg="#2C3E50",
                              bg="#FFFFFF")
        input_label.pack(anchor="w", pady=(0, 5))
        
        # Entry field
        entry_var = tk.StringVar(value=actual_license_name if actual_license_name else "")
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
            dialog_result_queue.put(None)
            dialog.destroy()
        
        def on_ok():
            result = entry_var.get().strip()
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
        
        ok_btn = tk.Button(button_frame,
                          text="Override & Continue",
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
        print(f"Dialog creation error: {e}")
        dialog_result_queue.put(None)

def get_manual_name_input(expected_name, actual_license_name, status_callback):
    """Thread-safe manual name input dialog"""
    dialog_result = queue.Queue()
    
    # Execute in main thread using the GUI's root window
    if hasattr(status_callback, '__self__') and hasattr(status_callback.__self__, 'root'):
        # Use the existing GUI root
        gui_root = status_callback.__self__.root
        gui_root.after(0, lambda: show_manual_input_dialog(expected_name, actual_license_name, dialog_result))
    else:
        # Fallback: create temporary root
        temp_root = tk.Tk()
        temp_root.withdraw()
        temp_root.after(0, lambda: show_manual_input_dialog(expected_name, actual_license_name, dialog_result))
    
    # Wait for result
    try:
        manual_name = dialog_result.get(timeout=60)  # 1 minute timeout
        return manual_name
    except queue.Empty:
        return None
