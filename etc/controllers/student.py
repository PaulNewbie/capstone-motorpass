# controllers/student.py - FIXED key name for GUI callback
import os

from etc.services.hardware.fingerprint import *
from etc.services.hardware.led_control import *
from etc.services.hardware.buzzer_control import *
from etc.services.hardware.rpi_camera import force_camera_cleanup

from etc.services.helmet_infer import verify_helmet
from etc.services.license_reader import (
    _count_verification_keywords, 
    extract_text_from_image, 
    _detect_name_pattern,
    complete_verification_flow,
    auto_capture_license_rpi
)

# Import database operations
from database.db_operations import (
    get_student_time_status,
    record_time_in,
    record_time_out
)

from etc.controllers.auth.student_auth import authenticate_fingerprint, authenticate_fingerprint_with_time_tracking

from etc.utils.display_helpers import display_separator, display_verification_result
from etc.utils.gui_helpers import show_results_gui
from etc.utils.dialog_helpers import get_manual_name_input

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
    """Run verification steps with GUI status updates"""
    
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
            set_led_failed_fast_blink()
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
            set_led_failed_fast_blink()
            cleanup_buzzer()
            return {'verified': False, 'reason': 'Fingerprint authentication failed after 5 attempts'}
        
        status_callback({'fingerprint_status': 'VERIFIED'})
        status_callback({'user_info': user_info})
        
        # Check current status with correct user_id
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
                set_led_failed_fast_blink()
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
                set_led_failed_fast_blink()
                cleanup_buzzer()
                return {'verified': False, 'reason': 'License has expired'}
            
            # License is valid
            status_callback({'license_status': 'VALID'})
            
            # Step 3: Fixed License capture and verification with proper file handling
            status_callback({'current_step': '📄 Capturing license... (Check terminal for camera)'})

            print("\n" + "="*60)
            print("📄 LICENSE CAPTURE (Terminal Camera)")
            print("="*60)

            license_success = False
            final_result = None
            current_image_path = None  # Track current image for cleanup

            # Create proper fingerprint_info structure for license verification
            fingerprint_info = {
                'name': user_info.get('name', ''),
                'confidence': user_info.get('confidence', 100),
                'user_type': user_info.get('user_type', 'STUDENT'),
                'finger_id': user_info.get('finger_id', 'N/A')
            }

            for attempt in range(2):  # Two attempts max
                print(f"\n📷 License attempt {attempt + 1}/2")
                
                # Clean up previous image if exists (but NOT the current one we're processing)
                if attempt > 0 and current_image_path and os.path.exists(current_image_path):
                    try:
                        os.remove(current_image_path)
                    except:
                        pass
                
                current_image_path = auto_capture_license_rpi(
                    reference_name=user_info.get('name', ''),
                    fingerprint_info=fingerprint_info
                )
                
                if not current_image_path:
                    # Camera capture failed - likely Student Permit detected in preview
                    print("❌ Student Driver License likely detected in camera preview")
                    status_callback({'current_step': '❌ Student Driver License not allowed - Access denied'})
                    set_led_idle()
                    play_failure()
                    set_led_failed_fast_blink()
                    return {'verified': False, 'reason': 'Student Driver License not allowed'}
                
                try:
                    # Run verification flow
                    verification_result = complete_verification_flow(
                        image_path=current_image_path,
                        fingerprint_info=fingerprint_info,
                        helmet_verified=True,
                        license_expiration_valid=license_expiration_valid
                    )
                    
                    if verification_result:
                        # SUCCESS - License matched
                        license_success = True
                        break
                        
                    else:
                        # FAILED - Check if we should try again or go to manual input
                        if attempt == 0:
                            # First attempt failed - auto retry
                            print(f"⚠️ FIRST ATTEMPT FAILED - Auto-retrying...")
                            status_callback({'current_step': '🔄 Auto-retrying license scan...'})
                            continue
                        else:
                            # Second attempt failed - PRESERVE the image file for manual input
                            print(f"\n🤔 MANUAL INPUT OPTION:")
                            print(f"   Second attempt verification failed")
                            print(f"   Expected: {user_info.get('name', 'N/A')}")
                            
                            # Extract name from current image - file should still be accessible
                            display_name = "Processing error"
                            actual_license_name = None
                            
                            try:
                                if current_image_path and os.path.exists(current_image_path):
                                    print(f"   📁 Processing image: {os.path.basename(current_image_path)}")
                                    ocr_text = extract_text_from_image(current_image_path)
                                    actual_license_name = _detect_name_pattern(ocr_text)
                                    
                                    if actual_license_name:
                                        print(f"   Detected: {actual_license_name}")
                                        display_name = actual_license_name
                                    else:
                                        print(f"   Detected: No name found (scanning issue)")
                                        display_name = "No name detected"
                                else:
                                    print(f"   ❌ Image file not found: {current_image_path}")
                                    display_name = "File not found"
                                    
                            except Exception as e:
                                print(f"   ⚠️ Name extraction error: {e}")
                                display_name = "OCR processing error"
                            
                            # Show what we're working with
                            print(f"   📝 Manual input will show: '{display_name}'")
                            
                            # Process manual input attempts
                            manual_success = False
                            
                            # First manual input attempt
                            print(f"\n🔤 MANUAL INPUT ATTEMPT 1/2")
                            manual_name = get_manual_name_input(
                                user_info.get('name', 'N/A'),
                                display_name,
                                status_callback
                            )
                            
                            if manual_name and manual_name.strip():
                                manual_name = manual_name.strip().title()
                                expected_name = user_info.get('name', '').title()
                                
                                print(f"   👤 User entered: '{manual_name}'")
                                print(f"   🎯 Expected: '{expected_name}'")
                                
                                if manual_name == expected_name:
                                    # First manual input successful
                                    print(f"✅ Manual input successful on first attempt")
                                    manual_success = True
                                    final_result = {
                                        'verified': True,
                                        'name': user_info['name'],
                                        'time_action': 'IN',
                                        'manual_override': True,
                                        'manual_name': manual_name
                                    }
                                else:
                                    # First manual input failed - give second chance
                                    print(f"❌ Manual input attempt 1 failed: Names don't match")
                                    print(f"🔤 MANUAL INPUT ATTEMPT 2/2 (Last Chance)")
                                    
                                    second_manual_name = get_manual_name_input(
                                        user_info.get('name', 'N/A'),
                                        display_name,  # Show same detected name
                                        status_callback,
                                        attempt_number=2
                                    )
                                    
                                    if second_manual_name and second_manual_name.strip():
                                        second_manual_name = second_manual_name.strip().title()
                                        
                                        print(f"   👤 User entered: '{second_manual_name}'")
                                        print(f"   🎯 Expected: '{expected_name}'")
                                        
                                        if second_manual_name == expected_name:
                                            # Second manual input successful
                                            print(f"✅ Manual input successful on second attempt")
                                            manual_success = True
                                            final_result = {
                                                'verified': True,
                                                'name': user_info['name'],
                                                'time_action': 'IN',
                                                'manual_override': True,
                                                'manual_name': second_manual_name
                                            }
                                        else:
                                            # Both manual attempts failed
                                            print(f"❌ Manual input attempt 2 failed: Names don't match")
                                            print("❌ Manual override DENIED - Both attempts failed")
                                    else:
                                        # Second manual input cancelled
                                        print("❌ Manual input attempt 2 cancelled")
                            else:
                                # First manual input cancelled
                                print("❌ Manual input attempt 1 cancelled")
                            
                            # Clean up image file AFTER manual input processing
                            if current_image_path and os.path.exists(current_image_path):
                                try:
                                    os.remove(current_image_path)
                                    print(f"   🗑️ Cleaned up image file")
                                except:
                                    pass
                            
                            # Handle manual input results
                            if manual_success:
                                license_success = True
                                break
                            else:
                                return {'verified': False, 'reason': 'Manual override failed'}
                
                except ValueError as e:
                    if "STUDENT_PERMIT_DETECTED" in str(e):
                        status_callback({'current_step': '❌ Student Permit detected - Access denied'})
                        set_led_idle()
                        play_failure()
                        set_led_failed_fast_blink()
                        # Clean up and return failure
                        if current_image_path and os.path.exists(current_image_path):
                            try:
                                os.remove(current_image_path)
                            except:
                                pass
                        return {'verified': False, 'reason': 'Student Permit not allowed'}
                    else:
                        raise e

            # Final cleanup - only if we didn't already clean up during manual input
            if current_image_path and os.path.exists(current_image_path):
                try:
                    os.remove(current_image_path)
                    print(f"🗑️ Final cleanup of image file")
                except:
                    pass

            # Handle successful verification
            if license_success:
                # Use final_result if it was set by manual input, otherwise create standard result
                if final_result:
                    if record_time_in(user_info):
                        timestamp = time.strftime('%H:%M:%S')
                        status_callback({'current_step': f'✅ TIME IN recorded at {timestamp} (Manual Override)'})
                        final_result['timestamp'] = timestamp
                        set_led_success(duration=5.0)
                        play_success()
                        result = final_result
                    else:
                        status_callback({'current_step': '❌ Failed to record TIME IN'})
                        set_led_idle()
                        play_failure()
                        set_led_failed_fast_blink()
                        result = {'verified': False, 'reason': 'Failed to record TIME IN'}
                else:
                    # Standard verification success
                    verification_summary = {
                        'helmet': True,
                        'fingerprint': True,
                        'license_valid': license_expiration_valid,
                        'license_detected': True,
                        'name_match': True
                    }
                    status_callback({'verification_summary': verification_summary})
                    
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
                        set_led_failed_fast_blink()
                        result = {'verified': False, 'reason': 'Failed to record TIME IN'}

            # If we reach here, verification completely failed
            if not result.get('verified', False):
                result = {'verified': False, 'reason': 'License verification failed'}
    
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
