# etc/controllers/student.py 
"""
Student/Staff Verification Controller 
"""

import os
import time
from datetime import datetime

# Hardware imports
from etc.services.hardware.fingerprint import *
from etc.services.hardware.led_control import *
from etc.services.hardware.buzzer_control import *
from etc.services.hardware.rpi_camera import force_camera_cleanup

# Service imports
from etc.services.helmet_infer import verify_helmet
from etc.services.license_reader import (
    _count_verification_keywords, 
    extract_text_from_image, 
    _detect_name_pattern,
    complete_verification_flow,
    auto_capture_license_rpi
)

# Helper imports 
from etc.utils.led_helpers import execute_failure_feedback_concurrent
from etc.utils.verification_helpers import *
from etc.utils.message import *

# Database imports
from database.db_operations import (
    get_student_time_status,
    record_time_in,
    record_time_out
)

# Auth imports
from etc.controllers.auth.student_auth import authenticate_fingerprint
from etc.utils.dialog_helpers import get_manual_name_input


def student_verification():
    """Main student/staff verification with GUI"""
    print("\n🎓👔 STUDENT/STAFF VERIFICATION")
    print("🖥️ Opening GUI interface...")
    
    from etc.ui.student_gui import StudentVerificationGUI
    
    gui = StudentVerificationGUI(run_verification_with_gui)
    gui.run()


def run_verification_with_gui(status_callback):
    """
    Run verification steps with GUI status updates
    """
    
    # Initialize systems
    init_buzzer()
    set_led_processing()
    play_processing()
    
    # ========== STEP 1: HELMET VERIFICATION ==========
    if not _verify_helmet_step(status_callback):
        cleanup_buzzer()
        set_led_idle()
        return handle_verification_failure(
            status_callback, 
            MSG_HELMET_FAILED
        )
    
    # ========== STEP 2: FINGERPRINT VERIFICATION ==========
    user_info = _verify_fingerprint_step(status_callback)
    if not user_info:
        cleanup_buzzer()
        set_led_idle()
        return handle_verification_failure(
            status_callback,
            MSG_FINGERPRINT_FAILED
        )
    
    # ========== STEP 3: CHECK TIME STATUS ==========
    user_id = user_info.get('unified_id', user_info.get('student_id', ''))
    current_status = get_student_time_status(user_id)
    log_info(MSG_CURRENT_STATUS.format(name=user_info['name'], status=current_status))
    
    # ========== HANDLE TIME OUT (No license scan needed) ==========
    if current_status == 'IN':
        return _handle_time_out(status_callback, user_info)
    
    # ========== STEP 4: LICENSE VERIFICATION FOR TIME IN ==========
    license_expiration_valid = _check_license_expiration(user_info)
    
    if not license_expiration_valid:
        # Record expired attempt and deny access
        _record_expired_license_attempt(user_info)
        
        # Calculate days overdue with flexible date parsing
        days_overdue = 0
        try:
            expiration_date_str = user_info.get('license_expiration', '2000-01-01')
            try:
                exp_date = datetime.strptime(expiration_date_str, '%Y-%m-%d').date()
            except ValueError:
                exp_date = datetime.strptime(expiration_date_str, '%m/%d/%Y').date()
            days_overdue = (datetime.now().date() - exp_date).days
        except:
            days_overdue = 0
        
        cleanup_buzzer()
        set_led_idle()
        return handle_expired_license(
            status_callback, 
            user_info,
            days_overdue
        )
    
    # ========== STEP 5: LICENSE CAPTURE AND VERIFICATION ==========
    result = _verify_license_and_record_time_in(
        status_callback, 
        user_info, 
        license_expiration_valid
    )
    
    return result


# ============================================================================
# STEP FUNCTIONS - Organized by verification phase
# ============================================================================

def _verify_helmet_step(status_callback):
    """
    Step 1: Helmet verification
    Returns: bool - True if verified, False otherwise
    """
    status_callback({'current_step': MSG_CHECKING_HELMET})
    status_callback({'helmet_status': 'CHECKING'})
    
    print(f"\n{SEPARATOR_LONG}")
    print(MSG_HELMET_TERMINAL)
    print(SEPARATOR_LONG)
    
    if not verify_helmet():
        status_callback({'helmet_status': 'FAILED'})
        status_callback({'current_step': f'❌ {MSG_HELMET_FAILED}'})
        
        result_data = {'verified': False, 'reason': MSG_HELMET_FAILED}
        execute_failure_feedback_concurrent(status_callback, result_data)
        time.sleep(3.0)
        return False
    
    status_callback({'helmet_status': 'VERIFIED'})
    status_callback({'current_step': MSG_HELMET_VERIFIED})
    log_success("Helmet verification successful")
    return True


def _verify_fingerprint_step(status_callback):
    """
    Step 2: Fingerprint verification
    Returns: dict - User info if verified, None otherwise
    """
    status_callback({'current_step': MSG_CHECKING_FINGERPRINT})
    status_callback({'fingerprint_status': 'PROCESSING'})
    
    user_info = authenticate_fingerprint(max_attempts=3)
    
    if not user_info:
        status_callback({'fingerprint_status': 'FAILED'})
        status_callback({'current_step': f'❌ {MSG_FINGERPRINT_FAILED}'})
        
        result_data = {'verified': False, 'reason': MSG_FINGERPRINT_FAILED}
        execute_failure_feedback_concurrent(status_callback, result_data)
        time.sleep(3.0)
        return None
    
    status_callback({'fingerprint_status': 'VERIFIED'})
    status_callback({'user_info': user_info})
    return user_info


def _handle_time_out(status_callback, user_info):
    """
    Handle TIME OUT (skip license scanning)
    Returns: dict - Success result
    """
    status_callback({'current_step': MSG_PROCESSING_TIME_OUT})
    
    # Show simplified verification summary
    verification_summary = create_verification_summary(
        helmet=True,
        fingerprint=True,
        license_valid=True,
        license_detected=True,
        name_match=True
    )
    status_callback({'verification_summary': verification_summary})
    
    # Record TIME OUT
    if record_time_out(user_info):
        timestamp = handle_time_in_success(
            status_callback, 
            MSG_TIME_OUT_RECORDED.format(timestamp=time.strftime('%H:%M:%S'))
        )
        
        result = build_standard_success_result(user_info, timestamp, 'OUT')
        result['verified'] = True
        status_callback({'final_result': result})
        
        cleanup_buzzer()
        time.sleep(5.0)
        set_led_idle()
        return result
    else:
        cleanup_buzzer()
        set_led_idle()
        return handle_time_in_failure(status_callback)


def _check_license_expiration(user_info):
    try:
        expiration_date_str = user_info.get('license_expiration', '2000-01-01')
        
        # Try both date formats
        expiration_date = None
        
        # Try YYYY-MM-DD format first
        try:
            expiration_date = datetime.strptime(expiration_date_str, '%Y-%m-%d').date()
        except ValueError:
            # Try M/D/YYYY format (your database format)
            try:
                expiration_date = datetime.strptime(expiration_date_str, '%m/%d/%Y').date()
            except ValueError:
                log_error(f"Invalid date format: {expiration_date_str}")
                return False
        
        today = datetime.now().date()
        license_expiration_valid = expiration_date >= today
        
        if not license_expiration_valid:
            days_overdue = (today - expiration_date).days
            log_warning(f"License expired {days_overdue} days ago")
        
        return license_expiration_valid
        
    except Exception as e:
        log_error(f"Error checking license expiration: {e}")
        return False


def _record_expired_license_attempt(user_info):
    """Record expired license attempt to database using existing function"""
    try:
        # Import the existing function from db_operations
        from database.db_operations import log_expired_license_attempt
        
        expiration_date_str = user_info.get('license_expiration', '2000-01-01')
        
        # Parse date flexibly to calculate days overdue
        expiration_date = None
        try:
            expiration_date = datetime.strptime(expiration_date_str, '%Y-%m-%d').date()
        except ValueError:
            try:
                expiration_date = datetime.strptime(expiration_date_str, '%m/%d/%Y').date()
            except ValueError:
                log_warning(f"Could not parse date: {expiration_date_str}")
                return
        
        today = datetime.now().date()
        days_overdue = (today - expiration_date).days
        
        # Call your existing function with correct signature
        log_expired_license_attempt(user_info, days_overdue)
        log_info("Expired license attempt logged to database")
        
    except Exception as e:
        log_warning(f"Could not log expired license attempt: {e}")

def _verify_license_and_record_time_in(status_callback, user_info, license_expiration_valid):
    """
    Step 5: License capture, verification, and TIME IN recording
    Handles auto-retry and manual override workflow
    Returns: dict - Verification result
    """
    status_callback({'current_step': MSG_CHECKING_LICENSE})
    status_callback({'license_status': 'CHECKING'})
    
    print(f"\n{SEPARATOR_LONG}")
    print(MSG_LICENSE_TERMINAL)
    print(SEPARATOR_LONG)
    
    license_success = False
    final_result = None
    current_image_path = None
    
    # Create fingerprint_info structure
    fingerprint_info = {
        'name': user_info.get('name', ''),
        'confidence': user_info.get('confidence', 100),
        'user_type': user_info.get('user_type', 'STUDENT'),
        'finger_id': user_info.get('finger_id', 'N/A')
    }
    
    # Two attempts max
    for attempt in range(2):
        print(f"\n{MSG_LICENSE_ATTEMPT.format(attempt=attempt + 1)}")
        
        # Clean up previous image (not current)
        if attempt > 0 and current_image_path:
            cleanup_image_file(current_image_path)
        
        # Capture license
        capture_result = auto_capture_license_rpi(
            reference_name=user_info.get('name', ''),
            fingerprint_info=fingerprint_info
        )
        
        # Unpack result
        if isinstance(capture_result, tuple):
            current_image_path, reason = capture_result
        else:
            current_image_path = capture_result
            reason = "success" if current_image_path else "unknown"
        
        # Handle capture failures with clean helpers
        if not current_image_path:
            if reason == "student_permit":
                return handle_student_license_denied(status_callback)
            elif reason == "cancelled":
                return handle_license_capture_cancelled(status_callback)
            else:
                return handle_license_capture_error(status_callback, reason)
        
        # Check for Student Permit in verification
        try:
            verification_result = complete_verification_flow(
                image_path=current_image_path,
                fingerprint_info=fingerprint_info,
                helmet_verified=True,
                license_expiration_valid=license_expiration_valid
            )
            
            if verification_result:
                # SUCCESS!
                license_success = True
                status_callback({'license_status': 'VALID'})
                break
            else:
                # Failed verification
                if attempt == 0:
                    # First attempt - auto retry
                    log_warning(MSG_FIRST_ATTEMPT_FAILED)
                    status_callback({'current_step': MSG_AUTO_RETRY})
                    continue
                else:
                    # Second attempt - offer manual input
                    final_result = _handle_manual_input_workflow(
                        status_callback,
                        user_info,
                        current_image_path
                    )
                    
                    if final_result:
                        license_success = True
                        break
                    else:
                        return handle_manual_override_failure(status_callback, current_image_path)
        
        except ValueError as e:
            if "STUDENT_PERMIT_DETECTED" in str(e):
                return handle_student_permit_denied(status_callback, current_image_path)
            else:
                raise e
    
    # Final cleanup
    cleanup_image_file(current_image_path)
    
    # Handle successful verification
    if license_success:
        return _record_successful_time_in(
            status_callback,
            user_info,
            final_result,
            license_expiration_valid
        )
    
    return handle_verification_failure(status_callback, MSG_LICENSE_VERIFICATION_FAILED)


def _handle_manual_input_workflow(status_callback, user_info, image_path):
    """
    Handle manual input workflow for second attempt failure
    Returns: dict - Manual override result or None
    """
    log_warning(MSG_MANUAL_INPUT_OPTION)
    log_warning(MSG_SECOND_ATTEMPT_FAILED)
    log_info(MSG_EXPECTED_NAME.format(name=user_info.get('name', 'N/A')))
    
    # Extract name from license
    actual_license_name = _extract_name_from_image(image_path)
    
    if actual_license_name:
        display_name = actual_license_name
        log_info(MSG_DETECTED_NAME.format(name=actual_license_name))
    else:
        display_name = "Processing error"
        log_warning("Could not extract name from license")
    
    # Two manual input attempts
    for manual_attempt in range(1, 3):
        manual_success, manual_result = process_manual_input_workflow(
            status_callback=status_callback,
            user_info=user_info,
            actual_license_name=display_name,
            attempt_number=manual_attempt,
            get_manual_input_func=get_manual_name_input
        )
        
        if manual_success:
            return manual_result
        elif manual_result is None:
            # Cancelled
            continue
        else:
            # Name mismatch
            if manual_attempt == 2:
                log_error("❌ Manual override DENIED - Both attempts failed")
                break
    
    return None


def _extract_name_from_image(image_path):
    """
    Extract name from license image
    Returns: str - Detected name or None
    """
    try:
        if image_path and os.path.exists(image_path):
            log_info(MSG_PROCESSING_IMAGE.format(filename=os.path.basename(image_path)))
            ocr_text = extract_text_from_image(image_path)
            return _detect_name_pattern(ocr_text)
    except Exception as e:
        log_error(f"Error extracting name: {e}")
    return None


def _record_successful_time_in(status_callback, user_info, final_result, license_expiration_valid):
    """
    Record successful TIME IN after all verifications pass
    Returns: dict - Final success result
    """
    # Use manual override result if available
    if final_result:
        if record_time_in(user_info):
            timestamp = time.strftime('%H:%M:%S')
            status_callback({'current_step': f'{MSG_TIME_IN_RECORDED.format(timestamp=timestamp)} (Manual Override)'})
            final_result['timestamp'] = timestamp
            set_led_success(duration=5.0)
            play_success()
            result = final_result
        else:
            return handle_time_in_failure(status_callback)
    else:
        # Standard verification success
        verification_summary = create_verification_summary(
            helmet=True,
            fingerprint=True,
            license_valid=license_expiration_valid,
            license_detected=True,
            name_match=True
        )
        status_callback({'verification_summary': verification_summary})
        
        if record_time_in(user_info):
            timestamp = handle_time_in_success(status_callback)
            # ✅ FIXED LINE — use user_info only
            return build_standard_success_result(user_info, timestamp, 'IN')
        else:
            return handle_time_in_failure(status_callback)
    
    # Show final result
    status_callback({'final_result': result})
    
    cleanup_buzzer()
    time.sleep(5.0)
    set_led_idle()
    
    return result

