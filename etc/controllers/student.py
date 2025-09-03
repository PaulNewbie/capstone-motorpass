# controllers/student.py - FIXED key name for GUI callback

from etc.services.fingerprint import *
from etc.services.license_reader import *
from etc.services.helmet_infer import verify_helmet
from etc.services.led_control import *
from etc.services.buzzer_control import *
from etc.services.rpi_camera import force_camera_cleanup

# Import database operations
from database.db_operations import (
    get_student_time_status,
    record_time_in,
    record_time_out
)

from etc.utils.display_helpers import display_separator, display_verification_result
from etc.utils.gui_helpers import show_results_gui

import time
from datetime import datetime
import tkinter as tk
import tkinter.messagebox as msgbox
import threading 
import queue

def student_verification():
    """Main student/staff verification with GUI"""
    print("\n🎓👔 STUDENT/STAFF VERIFICATION")
    print("🖥️ Opening GUI interface...")
    
    # Import GUI here to avoid circular imports
    from etc.ui.student_gui import StudentVerificationGUI
    
    # Create and run GUI
    gui = StudentVerificationGUI(run_verification_with_gui)
    gui.run()

def run_verification_with_gui(status_callback):
    """Run verification steps with GUI status updates - COMPLETE VERSION"""
    
    # Initialize systems
    init_buzzer()
    set_led_processing()
    play_processing()
    
    # Initialize result variable
    result = {'verified': False, 'reason': 'Unknown error'}
    
    try:
        # Step 1: Helmet verification
        status_callback({'current_step': '🪖 Checking helmet... (Check terminal for camera)'})
        status_callback({'helmet_status': 'CHECKING'})
        
        print("\n" + "="*60)
        print("🪖 HELMET VERIFICATION (Terminal Camera)")
        print("="*60)
        
        if not verify_helmet():
            status_callback({'helmet_status': 'FAILED'})
            status_callback({'current_step': '❌ Helmet verification failed'})
            set_led_idle()
            play_failure()
            cleanup_buzzer()
            return {'verified': False, 'reason': 'Helmet verification failed'}
        
        status_callback({'helmet_status': 'VERIFIED'})
        status_callback({'current_step': '✅ Helmet verified successfully!'})
        print("✅ Helmet verification successful")
        
        # Step 2: Fingerprint verification
        status_callback({'current_step': '🔍 Please place your finger on the scanner'})
        status_callback({'fingerprint_status': 'PROCESSING'})

        user_info = authenticate_fingerprint(max_attempts=5)
        
        if not user_info:
            status_callback({'fingerprint_status': 'FAILED'})
            status_callback({'current_step': '❌ Fingerprint authentication failed - Access Denied'})
            set_led_idle()
            play_failure()
            cleanup_buzzer()
            return {'verified': False, 'reason': 'Fingerprint authentication failed after 5 attempts'}
        
        status_callback({'fingerprint_status': 'VERIFIED'})
        status_callback({'user_info': user_info})
        
        # FIXED: Check current status with correct user_id
        user_id = user_info.get('unified_id', user_info.get('student_id', ''))
        current_status = get_student_time_status(user_id)
        
        print(f"🔍 Current status for {user_info['name']}: {current_status}")
        
        # Simple logic: Skip license scan if timing out
        if current_status == 'IN':
            # TIME OUT - Skip license scanning
            status_callback({'current_step': '🚪 Processing TIME OUT - No license scan needed'})
            
            # Show simplified verification summary
            verification_summary = {
                'helmet': True,
                'fingerprint': True,
                'license_valid': True,  # Skip for TIME OUT
                'license_detected': True,  # Skip for TIME OUT
                'name_match': True  # Already verified by fingerprint
            }
            status_callback({'verification_summary': verification_summary})
            
            # Record TIME OUT directly
            if record_time_out(user_info):
                timestamp = time.strftime('%H:%M:%S')
                status_callback({'current_step': f'✅ TIME OUT recorded at {timestamp}'})
                set_led_success(duration=5.0)
                play_success()
                
                result = {
                    'verified': True,
                    'name': user_info['name'],
                    'time_action': 'OUT',
                    'timestamp': timestamp,
                    'student_id': user_info.get('student_id', 'N/A')
                }
            else:
                status_callback({'current_step': '❌ Failed to record TIME OUT'})
                set_led_idle()
                play_failure()
                result = {'verified': False, 'reason': 'Failed to record TIME OUT'}
                
        else:
            # TIME IN - Do full verification with license scan
            status_callback({'current_step': '📄 Processing TIME IN - License scan required'})
            
            # Step 2.5: Process license expiration data
            license_expiration_valid = False
            days_left = 0
            
            if 'days_until_expiration' in user_info:
                days_left = user_info['days_until_expiration']
                license_expiration_valid = days_left >= 0
            elif 'license_expiration' in user_info:
                license_expiration_valid = check_license_expiration(user_info)
                if license_expiration_valid:
                    days_left = 30  # Default for valid
                else:
                    days_left = -1  # Default for expired
            else:
                license_expiration_valid = True  # Default if no expiration data
                days_left = 365  # Default
            
            # Update GUI with license status
            status_callback({
                'license_info': {
                    'number': user_info.get('license_number', 'N/A'),
                    'expiration_date': user_info.get('license_expiration', 'N/A')
                }
            })
            
            # Check if license has expired
            if not license_expiration_valid:
                status_callback({
                    'license_status': 'EXPIRED',
                    'current_step': f'❌ License expired ({abs(days_left)} days overdue)'
                })
                set_led_idle()
                play_failure()
                cleanup_buzzer()
                return {'verified': False, 'reason': 'License has expired'}
            
            # License is valid
            status_callback({'license_status': 'VALID'})
            
            # Step 3: License capture and verification
            status_callback({'current_step': '📄 Capturing license... (Check terminal for camera)'})
            
            print("\n" + "="*60)
            print("📄 LICENSE CAPTURE (Terminal Camera)")
            print("="*60)
            
            from etc.services.license_reader import _count_verification_keywords, extract_text_from_image, _detect_name_pattern
            license_success = False
            image_path = None
            actual_license_name = None  # Track detected name across attempts
            
            for attempt in range(2):  # Try twice
                print(f"\n📷 License attempt {attempt + 1}/2")
                
                # FIXED: Create proper fingerprint_info structure for license verification
                fingerprint_info = {
                    'name': user_info.get('name', ''),  # This is the reference name from fingerprint
                    'confidence': user_info.get('confidence', 100),
                    'user_type': user_info.get('user_type', 'STUDENT'),
                    'finger_id': user_info.get('finger_id', 'N/A')
                }
                
                image_path = auto_capture_license_rpi(
                    reference_name=user_info.get('name', ''),
                    fingerprint_info=fingerprint_info  # Pass properly formatted fingerprint_info
                )
                
                if image_path:
                    # Student Permit check is now handled in license_reader.py
                    try:
                        ocr_text = extract_text_from_image(image_path)
                    except ValueError as e:
                        if "STUDENT_PERMIT_DETECTED" in str(e):
                            print("❌ Student Permit detected - Access denied")
                            status_callback({'current_step': '❌ Student Permit not allowed - Access denied'})
                            set_led_idle()
                            play_failure()
                            cleanup_buzzer()
                            return {'verified': False, 'reason': 'Student Permit not allowed'}
                        else:
                            raise e
                    
                    keywords_found = _count_verification_keywords(ocr_text)
                    
                    # OPTIMIZED: Get the actual name on the license (like guest flow)
                    ocr_lines = [line.strip() for line in ocr_text.splitlines() if line.strip()]
                    actual_license_name = _detect_name_pattern(ocr_text)
                    
                    # NEW: Clear terminal output showing actual vs expected names
                    print(f"\n📋 LICENSE SCAN RESULTS (Attempt {attempt + 1}/2):")
                    print(f"🎯 Expected Name: '{user_info.get('name', 'N/A')}'")
                    print(f"🔍 License Holder: '{actual_license_name if actual_license_name else 'NOT FOUND'}'")
                    print(f"📄 Keywords Found: {keywords_found}")
                    
                    # Check if names match (basic comparison)
                    name_matches = False
                    name_found = actual_license_name is not None and actual_license_name.strip() != ""
                    similarity_score = 0.0
                    
                    if actual_license_name and user_info.get('name'):
                        # Calculate similarity directly
                        import difflib
                        similarity_score = difflib.SequenceMatcher(
                            None, 
                            actual_license_name.lower().strip(), 
                            user_info.get('name', '').lower().strip()
                        ).ratio()
                        
                        # Consider it a match if very high similarity (90%+) or exact match
                        if similarity_score >= 0.9:
                            name_matches = True
                            print(f"✅ STRONG MATCH: {similarity_score*100:.1f}% similarity")
                        else:
                            print(f"⚠️ NAME MISMATCH: {similarity_score*100:.1f}% similarity")
                            print(f"   Expected: {user_info.get('name', '')}")
                            print(f"   License:  {actual_license_name}")
                    elif not name_found:
                        print(f"❌ NO NAME DETECTED: Could not extract name from license")
                    
                    # SUCCESS CONDITIONS: Name match overrides keyword requirement
                    has_good_keywords = keywords_found >= 3
                    has_some_keywords = keywords_found >= 1
                    perfect_conditions = has_some_keywords and name_found and name_matches
                    
                    if perfect_conditions:
                        # SUCCESS: Name matches (even with few keywords)
                        print(f"✅ License accepted: Strong name match ({similarity_score*100:.1f}%) overrides keyword requirement")
                        print(f"🎯 SUCCESS: Name match confirmed with {keywords_found} keywords")
                        license_success = True
                        break
                    
                    # AUTO-RETRY CONDITIONS (First attempt)
                    elif attempt == 0:
                        # Retry for ANY imperfect condition
                        retry_reasons = []
                        if not has_some_keywords:
                            retry_reasons.append(f"only {keywords_found} keywords (need at least 1)")
                        elif not has_good_keywords and not name_matches:
                            retry_reasons.append(f"only {keywords_found} keywords (need 3+ when name doesn't match)")
                        if not name_found:
                            retry_reasons.append("no name detected")
                        elif not name_matches and has_some_keywords:
                            retry_reasons.append(f"name mismatch ({similarity_score*100:.1f}% similarity)")
                        
                        print(f"⚠️ RETRY NEEDED: {', '.join(retry_reasons)}")
                        print(f"🔄 AUTO-RETRYING: Second attempt starting...")
                        status_callback({'current_step': '🔄 Auto-retrying license scan...'})
                        
                    else:  # Second attempt - more lenient acceptance
                        if has_some_keywords and name_found:
                            if name_matches:
                                print(f"✅ License accepted: Name match ({similarity_score*100:.1f}%) + {keywords_found} keywords (2nd attempt)")
                                print(f"🎯 SUCCESS: Name confirmed on second attempt")
                            else:
                                print(f"✅ License accepted: {keywords_found} keywords + name detected (2nd attempt)")
                                print(f"📄 SUCCESS: Valid license detected (name verification in next stage)")
                            license_success = True
                            break
                        else:
                            # Still not good enough after 2 attempts
                            print(f"⚠️ SECOND ATTEMPT FAILED:")
                            if not has_some_keywords and not name_found:
                                print(f"   - Only {keywords_found} keywords (need at least 1)")
                                print(f"   - No name detected")
                            elif not has_some_keywords:
                                print(f"   - Only {keywords_found} keywords (need at least 1)")
                            elif not name_found:
                                print(f"   - Name detection failed")
                            
                            print("❌ Both automatic attempts failed")
                            # Will offer manual input after the loop
                        
                else:
                    # Camera capture failed 
                    print(f"❌ Camera capture failed on attempt {attempt + 1}")
                    if attempt == 0:  # First attempt failed
                        print("❌ Student Driver License likely detected in camera preview")
                        status_callback({'current_step': '❌ Student Driver License not allowed - Access denied'})
                        set_led_idle()
                        play_failure()
                        cleanup_buzzer()
                        return {'verified': False, 'reason': 'Student Driver License not allowed'}
                    # Second attempt camera failure continues to manual input

            # ENHANCED: Manual input option after 2 failed attempts
            if not license_success:
                # Check if we have ANY valid license data from either attempt
                last_attempt_had_keywords = keywords_found >= 1  # At least 1 keyword indicates a license
                
                if last_attempt_had_keywords:
                    # We detected a license but quality was poor - offer manual input
                    print(f"\n🤔 MANUAL INPUT OPTION:")
                    print(f"   License detected but scan quality insufficient")
                    print(f"   Expected: {user_info.get('name', 'N/A')}")
                    if actual_license_name:
                        print(f"   Detected: {actual_license_name}")
                    
                    if msgbox.askyesno("Manual Input", 
                                     f"License scan quality insufficient.\n\n"
                                     f"Expected: {user_info.get('name', 'N/A')}\n"
                                     f"Detected: {actual_license_name if actual_license_name else 'Not found'}\n\n"
                                     f"Enter name manually?"):
                        
                        from etc.utils.gui_helpers import get_user_input_gui
                        
                        expected_name = user_info.get('name', 'N/A')
                        manual_name = get_user_input_gui(
                            f"Expected: {expected_name}\n\nEnter name from license:",
                            "Manual License Input",
                            expected_name
                        )
                        
                        if manual_name and manual_name.strip():
                            manual_name = manual_name.strip().title()
                            print(f"✅ Manual license input: {manual_name}")
                            
                            # Record TIME IN with manual input
                            if record_time_in(user_info):
                                timestamp = time.strftime('%H:%M:%S')
                                status_callback({'current_step': f'✅ TIME IN recorded at {timestamp} (Manual Input)'})
                                set_led_success(duration=5.0)
                                play_success()
                                
                                result = {
                                    'verified': True,
                                    'name': user_info['name'],
                                    'time_action': 'IN',
                                    'timestamp': timestamp,
                                    'manual_input': True,
                                    'manual_name': manual_name
                                }
                                cleanup_buzzer()
                                return result
                            else:
                                status_callback({'current_step': '❌ Failed to record time'})
                                set_led_idle()
                                play_failure()
                                cleanup_buzzer()
                                return {'verified': False, 'reason': 'Failed to record time'}
                        else:
                            print("❌ Manual input cancelled or empty")
                            cleanup_buzzer()
                            return {'verified': False, 'reason': 'Manual input cancelled'}
                    else:
                        cleanup_buzzer()
                        return {'verified': False, 'reason': 'Manual input declined'}
                else:
                    # No license detected at all - just fail
                    print("❌ No valid license detected in either attempt")
                    cleanup_buzzer()
                    return {'verified': False, 'reason': 'No valid license detected'}

            # ONLY run verification flow if license captured successfully
            if license_success and image_path:
                status_callback({'current_step': '🔍 Verifying license against fingerprint...'})
                
                # FIXED: Pass the properly formatted fingerprint_info
                try:
                    verification_result = complete_verification_flow(
                        image_path=image_path,
                        fingerprint_info=fingerprint_info,  # Use the properly formatted fingerprint_info
                        helmet_verified=True,
                        license_expiration_valid=license_expiration_valid
                    )
                except ValueError as e:
                    if "STUDENT_PERMIT_DETECTED" in str(e):
                        status_callback({'current_step': '❌ Student Driver License detected - Access denied'})
                        set_led_idle()
                        play_failure()
                        cleanup_buzzer()
                        return {'verified': False, 'reason': 'Student Driver License not allowed'}
                    else:
                        raise e
                
                # Show verification summary
                verification_summary = {
                    'helmet': True,
                    'fingerprint': True,
                    'license_valid': license_expiration_valid,
                    'license_detected': verification_result,
                    'name_match': verification_result
                }
                status_callback({'verification_summary': verification_summary})
                
                if verification_result:
                    # Record TIME IN
                    if record_time_in(user_info):
                        timestamp = time.strftime('%H:%M:%S')
                        status_callback({'current_step': f'✅ TIME IN recorded at {timestamp}'})
                        set_led_success(duration=5.0)
                        play_success()
                        
                        result = {
                            'verified': True,
                            'name': user_info['name'],
                            'time_action': 'IN',
                            'timestamp': timestamp,
                            'student_id': user_info.get('student_id', 'N/A')
                        }
                    else:
                        status_callback({'current_step': '❌ Failed to record TIME IN'})
                        set_led_idle()
                        play_failure()
                        result = {'verified': False, 'reason': 'Failed to record TIME IN'}
                else:
                    print("\n🤔 VERIFICATION FAILED - OPENING MANUAL INPUT DIALOG:")
                    print("   License detected but names don't match closely enough")
                    print(f"   Expected: {user_info.get('name', 'N/A')}")
                    if actual_license_name:
                        print(f"   License shows: {actual_license_name}")
                    
                    print("🔍 DEBUG: Creating professional manual input dialog...")
                    
                    try:
                        # Thread-safe manual input dialog
                        import tkinter as tk
                        from tkinter import messagebox
                        import queue
                        import threading
                        
                        # Create result queue
                        dialog_result = queue.Queue()
                        
                        def show_manual_input_dialog():
                            """Create a professional manual input dialog in main thread"""
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
                                tk.Label(expected_frame, text=user_info.get('name', 'N/A'),
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
                                    dialog_result.put(None)
                                    dialog.destroy()
                                
                                def on_ok():
                                    result = entry_var.get().strip()
                                    dialog_result.put(result)
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
                                dialog_result.put(None)
                        
                        # Execute in main thread using the GUI's root window
                        if hasattr(status_callback, '__self__') and hasattr(status_callback.__self__, 'root'):
                            # Use the existing GUI root
                            gui_root = status_callback.__self__.root
                            gui_root.after(0, show_manual_input_dialog)
                        else:
                            # Fallback: create temporary root
                            temp_root = tk.Tk()
                            temp_root.withdraw()
                            temp_root.after(0, show_manual_input_dialog)
                        
                        # Wait for result
                        try:
                            manual_name = dialog_result.get(timeout=60)  # 1 minute timeout
                            print(f"🔍 DEBUG: Dialog result: '{manual_name}'")
                        except queue.Empty:
                            manual_name = None
                            print("🔍 DEBUG: Dialog timed out")
                        
                        # Process result
                        manual_attempts = 0
                        max_manual_attempts = 2
                        manual_success = False
                        
                        while manual_attempts < max_manual_attempts and not manual_success:
                            manual_attempts += 1
                            
                            if manual_name and manual_name.strip():
                                manual_name = manual_name.strip().title()
                                expected_name = user_info.get('name', '').title()
                                
                                print(f"🔍 DEBUG: Manual attempt {manual_attempts}/{max_manual_attempts}")
                                print(f"🔍 DEBUG: Manual input: '{manual_name}'")
                                print(f"🔍 DEBUG: Expected: '{expected_name}'")
                                
                                # Check if names match exactly
                                if manual_name == expected_name:
                                    print(f"✅ Manual override accepted: Names match exactly")
                                    manual_success = True
                                    
                                    if record_time_in(user_info):
                                        timestamp = time.strftime('%H:%M:%S')
                                        status_callback({'current_step': f'✅ TIME IN recorded at {timestamp} (Manual Override)'})
                                        set_led_success(duration=5.0)
                                        play_success()
                                        
                                        result = {
                                            'verified': True,
                                            'name': user_info['name'],
                                            'time_action': 'IN',
                                            'timestamp': timestamp,
                                            'manual_override': True,
                                            'manual_name': manual_name
                                        }
                                        print(f"🎉 SUCCESS: Manual override completed!")
                                    else:
                                        status_callback({'current_step': '❌ Failed to record time'})
                                        set_led_idle()
                                        play_failure()
                                        result = {'verified': False, 'reason': 'Failed to record time'}
                                else:
                                    # Name doesn't match
                                    print(f"❌ Manual attempt {manual_attempts} failed: Name doesn't match")
                                    print(f"   Expected: '{expected_name}'")
                                    print(f"   Entered:  '{manual_name}'")
                                    
                                    if manual_attempts < max_manual_attempts:
                                        print(f"🔄 Giving second chance... (attempt {manual_attempts + 1}/{max_manual_attempts})")
                                        
                                        # Show dialog again for second attempt
                                        dialog_result.queue.clear()  # Clear previous result
                                        
                                        if hasattr(status_callback, '__self__') and hasattr(status_callback.__self__, 'root'):
                                            gui_root = status_callback.__self__.root
                                            gui_root.after(0, show_manual_input_dialog)
                                        else:
                                            temp_root = tk.Tk()
                                            temp_root.withdraw()
                                            temp_root.after(0, show_manual_input_dialog)
                                        
                                        # Wait for second attempt
                                        try:
                                            manual_name = dialog_result.get(timeout=60)
                                            print(f"🔍 DEBUG: Second attempt result: '{manual_name}'")
                                        except queue.Empty:
                                            manual_name = None
                                            print("🔍 DEBUG: Second attempt timed out")
                                            break
                                    else:
                                        # Both attempts failed
                                        status_callback({'current_step': '❌ Manual override failed after 2 attempts'})
                                        set_led_idle()
                                        play_failure()
                                        result = {'verified': False, 'reason': 'Manual override failed - name mismatch after 2 attempts'}
                            else:
                                # User cancelled
                                print(f"❌ Manual attempt {manual_attempts} cancelled")
                                status_callback({'current_step': '❌ Manual override cancelled'})
                                set_led_idle()
                                play_failure()
                                result = {'verified': False, 'reason': 'Manual override cancelled'}
                                break
                    
                    except Exception as e:
                        print(f"❌ ERROR in manual override: {e}")
                        import traceback
                        traceback.print_exc()
                        status_callback({'current_step': '❌ Manual override failed'})
                        set_led_idle()
                        play_failure()
                        result = {'verified': False, 'reason': f'Manual override error: {str(e)}'}
                    
                    print("🔍 DEBUG: Manual override completed")
    
    finally:
        cleanup_buzzer()
        
    return result
         
def check_license_expiration(user_info):
    """Check if license is expired"""
    try:
        expiration_date_str = user_info.get('license_expiration', '')
        if not expiration_date_str:
            return True  # No expiration date, assume valid
        
        # Try different date formats
        try:
            expiration_date = datetime.strptime(expiration_date_str, '%Y-%m-%d')
        except ValueError:
            try:
                expiration_date = datetime.strptime(expiration_date_str, '%m/%d/%Y')
            except ValueError:
                try:
                    expiration_date = datetime.strptime(expiration_date_str, '%d/%m/%Y')
                except ValueError:
                    print(f"❌ Unknown date format: {expiration_date_str}")
                    return True  # Can't parse, assume valid
        
        current_date = datetime.now()
        return expiration_date.date() >= current_date.date()
        
    except Exception as e:
        print(f"❌ Error checking license expiration: {e}")
        return True  # Error checking, assume valid
