# controllers/guest.py - FINAL FIXED: Cancel + Manual name + Correct function calls

from etc.services.license_reader import *
from etc.services.helmet_infer import verify_helmet
from etc.services.hardware.led_control import *  
from etc.services.hardware.buzzer_control import *
from etc.services.hardware.rpi_camera import force_camera_cleanup
from etc.utils.display_helpers import display_separator, display_verification_result
from etc.utils.gui_helpers import show_results_gui, get_guest_info_gui, updated_guest_office_gui
from etc.utils.timeout_security import timeout_security_verification
import difflib
import time

from etc.utils.led_helpers import *
from etc.utils.verification_helpers import (
    log_success, log_error, log_warning, log_info,
    cleanup_image_file,
    handle_verification_failure,
    handle_time_in_success,
    handle_student_permit_denied,
    build_standard_success_result,
    create_verification_summary
)
from etc.utils.message import (
    MSG_HELMET_TERMINAL, MSG_HELMET_FAILED, MSG_HELMET_VERIFIED,
    MSG_LICENSE_TERMINAL, MSG_LICENSE_VERIFICATION_FAILED,
    MSG_STUDENT_PERMIT_DENIED,
    SEPARATOR_LONG
)

from concurrent.futures import ThreadPoolExecutor
import threading

from etc.utils.firebase_helper import sync_guest_to_firebase

from database.db_operations import (
    add_guest,
    get_guest_time_status,
    get_guest_from_database,
    create_guest_time_data, 
    process_guest_time_in,
    process_guest_time_out
)


# ============================================================================
#                          MAIN ENTRY POINTS
# ============================================================================

def guest_verification():
    """Main guest verification with GUI"""
    log_info("GUEST VERIFICATION")
    log_info("Opening GUI interface...")
    
    from etc.ui.guest_gui import GuestVerificationGUI
    
    gui = GuestVerificationGUI(run_guest_verification_with_gui)
    gui.run()


def run_guest_verification_with_gui(status_callback):
    """
    Simplified guest verification with automatic timeout.
    Refactored to use step functions for clarity.
    """
    # Initialize systems
    init_buzzer()
    set_led_processing()
    play_processing()
    
    # Step 1: Helmet verification
    if not _verify_helmet_step(status_callback):
        return handle_verification_failure(
            status_callback, 
            'Helmet verification failed'
        )
    
    # Step 2: License capture and processing loop
    return _license_capture_and_processing_loop(status_callback)

# ============================================================================
#                          STEP FUNCTIONS
# ============================================================================

def _verify_helmet_step(status_callback):
    """Step 1: Verify helmet"""
    status_callback({'current_step': '🪖 Checking helmet... (Check terminal for camera)'})
    status_callback({'helmet_status': 'CHECKING'})
    
    print(f"\n{SEPARATOR_LONG}")
    print(MSG_HELMET_TERMINAL)
    print(SEPARATOR_LONG)
    
    if not verify_helmet():
        status_callback({'helmet_status': 'FAILED'})
        status_callback({'current_step': MSG_HELMET_FAILED})
        log_error("Helmet verification failed")
        return False
    
    status_callback({'helmet_status': 'VERIFIED'})
    status_callback({'current_step': MSG_HELMET_VERIFIED})
    log_success("Helmet verification successful")
    return True


def _license_capture_and_processing_loop(status_callback):
    """
    Step 2: Main license capture loop.
    Handles both new guest registration and automatic timeout.
    """
    while True:
        # Capture license - NOW WITH CANCEL DETECTION
        capture_result = _capture_license_step(status_callback)
        
        # FIX 1: Handle tuple return for cancellation
        if isinstance(capture_result, tuple):
            image_path, reason = capture_result
        else:
            image_path = capture_result
            reason = "success" if capture_result else "unknown"
        
        # Check if user cancelled
        if not image_path:
            if reason == "cancelled":
                log_warning("User cancelled license capture")
                status_callback({'current_step': '❌ License capture cancelled'})
                return handle_verification_failure(
                    status_callback,
                    'License capture cancelled by user'
                )
            else:
                return handle_verification_failure(
                    status_callback, 
                    'License capture failed'
                )
        
        status_callback({'license_status': 'DETECTED'})
        
        # Extract and verify name
        status_callback({'current_step': '🔍 Processing license information...'})
        
        # Check for Student Permit
        if _check_student_permit(image_path, status_callback):
            cleanup_image_file(image_path)
            return handle_student_permit_denied(status_callback)
        
        # Extract name
        detected_name = _extract_name_from_license(image_path)
        log_info(f"Detected name: {detected_name}")
        
        # Check if student/staff trying to enter as guest
        if _check_if_student_or_staff(detected_name, image_path, status_callback):
            cleanup_image_file(image_path)
            return handle_verification_failure(
                status_callback,
                'Student/Staff not allowed as visitors'
            )
        
        # Check guest status
        current_status, guest_info = get_guest_time_status(detected_name)
        
        if current_status == 'IN':
            # Automatic timeout for existing guest
            return _handle_automatic_timeout(
                detected_name, 
                guest_info, 
                image_path, 
                status_callback
            )
        else:
            # New guest registration
            return _handle_new_guest_registration(
                detected_name, 
                image_path, 
                status_callback
            )


def _capture_license_step(status_callback):
    """Step 2a: Capture license with cancel detection"""
    status_callback({'current_step': '📄 Capturing license... (Check terminal for camera)'})
    status_callback({'license_status': 'PROCESSING'})
    
    print(f"\n{SEPARATOR_LONG}")
    print(MSG_LICENSE_TERMINAL)
    print(SEPARATOR_LONG)
    
    # FIX 1: Capture returns tuple (image_path, reason)
    capture_result = auto_capture_license_rpi()
    
    # Handle tuple return
    if isinstance(capture_result, tuple):
        image_path, reason = capture_result
        
        if not image_path and reason == "cancelled":
            status_callback({'license_status': 'CANCELLED'})
            status_callback({'current_step': '❌ License capture cancelled'})
            log_warning("License capture cancelled by user")
            return None, "cancelled"
        elif not image_path:
            status_callback({'license_status': 'FAILED'})
            status_callback({'current_step': MSG_LICENSE_VERIFICATION_FAILED})
            log_error("License capture failed")
            return None, reason
        
        return image_path, "success"
    else:
        # Old format compatibility
        image_path = capture_result
        if not image_path:
            status_callback({'license_status': 'FAILED'})
            status_callback({'current_step': MSG_LICENSE_VERIFICATION_FAILED})
            log_error("License capture failed")
        
        return image_path


def _check_student_permit(image_path, status_callback):
    """Check if license is a student permit"""
    try:
        extract_text_from_image(image_path)
        return False
    except ValueError as e:
        if "STUDENT_PERMIT_DETECTED" in str(e):
            log_error("Student Permit detected - Access denied")
            status_callback({'current_step': MSG_STUDENT_PERMIT_DENIED})
            return True
        raise e


def _extract_name_from_license(image_path):
    """Extract guest name from license OCR"""
    ocr_preview = extract_text_from_image(image_path)
    ocr_lines = [line.strip() for line in ocr_preview.splitlines() if line.strip()]
    return extract_guest_name_from_license(ocr_lines)


def _check_if_student_or_staff(detected_name, image_path, status_callback):
    """Check if detected name matches student/staff in database"""
    is_student_staff, match_info = check_if_student_or_staff_name(detected_name)
    
    if is_student_staff:
        log_error(f"Student/Staff detected as visitor - Access DENIED")
        log_info(f"Match found: {match_info}")
        status_callback({
            'current_step': f'❌ Student/Staff NOT allowed as visitors - {match_info}'
        })
        return True
    
    return False

def _handle_automatic_timeout(detected_name, guest_info, image_path, status_callback):
    """Handle automatic timeout for guest already in system"""
    log_info(f"Guest '{detected_name}' already IN - Processing automatic TIMEOUT")
    
    # Extract guest information
    guest_name = guest_info.get('name', detected_name)
    guest_plate = guest_info.get('plate_number', 'N/A')
    guest_office = guest_info.get('office', 'N/A')
    
    status_callback({
        'guest_info': {
            'name': guest_name,
            'plate_number': guest_plate,
            'office': guest_office,
            'status': 'AUTOMATIC TIMEOUT'
        }
    })
    
    status_callback({'current_step': '🔒 Security verification required for timeout...'})
    
    # FIX: Pass the whole guest_info dict, not just the name
    security_result = timeout_security_verification(guest_info)
    
    # FIX: security_result is a boolean (True/False), not a dict
    if security_result:
        log_success("Security verification passed - Processing TIMEOUT")
        return _process_guest_timeout(guest_info, image_path, status_callback)
    else:
        log_error("Security verification failed or cancelled")
        status_callback({'current_step': '❌ Security verification failed - Timeout DENIED'})
        cleanup_image_file(image_path)
        return handle_verification_failure(
            status_callback,
            'Security verification failed'
        )


def _process_guest_timeout(guest_info, image_path, status_callback):
    """Process guest timeout after security verification"""
    status_callback({'current_step': '📝 Recording TIME OUT...'})
    
    time_result = process_guest_time_out(guest_info)
    
    if time_result['success']:
        timestamp = time.strftime('%H:%M:%S')
        status_callback({'current_step': f'✅ TIME OUT recorded at {timestamp}'})
        
        set_led_success(duration=5.0)
        play_success()
        
        status_callback({
            'verification_summary': {
                'helmet': True,
                'license': True
            }
        })
        
        cleanup_buzzer()
        cleanup_image_file(image_path)
        
        # FIX: Return complete guest information in success result
        return {
            'verified': True,
            'name': guest_info.get('name', 'Guest'),
            'student_id': guest_info.get('guest_number', guest_info.get('plate_number', 'N/A')),
            'user_type': 'GUEST',
            'time_action': 'OUT',
            'timestamp': timestamp,
            'plate_number': guest_info.get('plate_number', 'N/A'),
            'office': guest_info.get('office', 'N/A'),
            'guest_number': guest_info.get('guest_number', 'N/A')
        }
    else:
        status_callback({'current_step': '❌ Failed to record TIME OUT'})
        cleanup_image_file(image_path)
        return handle_verification_failure(
            status_callback,
            'Failed to record TIME OUT'
        )
        
def _handle_new_guest_registration(detected_name, image_path, status_callback):
    """Handle registration flow for new guests"""
    status_callback({
        'guest_info': {
            'name': detected_name if detected_name != "Guest" else "New Guest",
            'status': 'NEW GUEST - REGISTRATION'
        }
    })
    
    status_callback({'current_step': '🔍 Please provide guest information...'})
    
    # Get guest info with retake functionality
    while True:
        guest_info_input = get_guest_info_gui(detected_name)
        
        if guest_info_input == 'retake':
            log_info("User requested license retake from registration form")
            status_callback({'current_step': '📄 Retaking license scan...'})
            cleanup_image_file(image_path)
            # Return to license capture
            return _license_capture_and_processing_loop(status_callback)
        
        elif not guest_info_input:
            # User cancelled
            status_callback({'current_step': '❌ Guest registration cancelled'})
            cleanup_image_file(image_path)
            return handle_verification_failure(
                status_callback,
                'Guest registration cancelled'
            )
        
        # The manual input is the authoritative source
        return _process_new_guest_time_in(
            guest_info_input,  # This contains the manually entered name
            image_path, 
            status_callback
        )


def _process_new_guest_time_in(guest_info_input, image_path, status_callback):
    """Process time in for new guest"""
    # FIX 2: Use the manually entered name from guest_info_input
    manual_name = guest_info_input['name']
    
    status_callback({
        'guest_info': {
            'name': manual_name,  # Use manual input name
            'plate_number': guest_info_input['plate_number'],
            'office': guest_info_input['office'],
            'status': 'NEW GUEST - PROCESSING'
        }
    })
    
    status_callback({'current_step': '🔍 Processing guest time in...'})
    
    # FIX 2: Use manual name for verification, not detected name
    guest_data_for_license = {
        'name': manual_name,  # Use manual input name
        'plate_number': guest_info_input['plate_number'],
        'office': guest_info_input['office'],
        'is_guest': True
    }
    
    log_info(f"Using manually entered name: {manual_name}")
    
    # Verify license with MANUAL NAME (not detected name)
    try:
        is_guest_verified = complete_guest_verification_flow(
            image_path=image_path,
            guest_info=guest_data_for_license,
            helmet_verified=True
        )
    except ValueError as e:
        if "STUDENT_PERMIT_DETECTED" in str(e):
            status_callback({'current_step': MSG_STUDENT_PERMIT_DENIED})
            cleanup_image_file(image_path)
            return handle_student_permit_denied(status_callback)
        raise e
    
    if is_guest_verified:
        # Store guest and process time in - using MANUAL NAME
        store_guest_in_database(guest_info_input)  # Already has manual name
        time_result = process_guest_time_in(guest_info_input)  # Already has manual name
        
        if time_result['success']:
            timestamp = time.strftime('%H:%M:%S')
            status_callback({'current_step': f'✅ TIME IN recorded at {timestamp}'})
            
            set_led_success(duration=5.0)
            play_success()
            
            status_callback({
                'verification_summary': {
                    'helmet': True,
                    'license': True
                }
            })
            
            cleanup_buzzer()
            cleanup_image_file(image_path)
            
            # FIX 3: Create user_info dict for build_standard_success_result
            guest_user_info = {
                'name': manual_name,
                'student_id': guest_info_input.get('plate_number', 'N/A'),
                'user_type': 'GUEST'
            }
            
            return build_standard_success_result(guest_user_info, timestamp, 'IN')
        else:
            status_callback({'current_step': '❌ Failed to record TIME IN'})
            cleanup_image_file(image_path)
            return handle_verification_failure(
                status_callback,
                'Failed to record TIME IN'
            )
    else:
        status_callback({'current_step': '❌ Guest verification failed'})
        cleanup_image_file(image_path)
        return handle_verification_failure(
            status_callback,
            'License verification failed'
        )

# HELPER FUNCTIONS
def check_if_student_or_staff_name(name):
    """Check if detected name matches any student or staff in database using fuzzy matching"""
    try:
        from database.db_operations import get_all_students, get_all_staff
    except ImportError:
        return False, None
    
    if not name or name == "Guest":
        return False, None
    
    SIMILARITY_THRESHOLD = 0.70
    
    # Check students
    try:
        students = get_all_students()
        for student in students:
            similarity = difflib.SequenceMatcher(
                None, 
                name.lower().strip(), 
                student['full_name'].lower().strip()
            ).ratio()
            
            if similarity >= SIMILARITY_THRESHOLD:
                return True, (
                    f"STUDENT: {student['full_name']} "
                    f"({student.get('student_id', 'N/A')}) - "
                    f"{similarity*100:.1f}% match"
                )
    except Exception:
        pass
    
    # Check staff
    try:
        staff = get_all_staff()
        for staff_member in staff:
            similarity = difflib.SequenceMatcher(
                None, 
                name.lower().strip(), 
                staff_member['full_name'].lower().strip()
            ).ratio()
            
            if similarity >= SIMILARITY_THRESHOLD:
                return True, (
                    f"STAFF: {staff_member['full_name']} "
                    f"({staff_member.get('staff_no', 'N/A')}) - "
                    f"{similarity*100:.1f}% match"
                )
    except Exception:
        pass
    
    return False, None


def store_guest_in_database(guest_info):
    """Store guest with safe Firebase sync"""
    try:
        guest_data = {
            'full_name': guest_info['name'],
            'plate_number': guest_info['plate_number'],
            'office_visiting': guest_info['office']
        }
        
        guest_number = add_guest(guest_data)
        
        if guest_number:
            log_success(f"Guest record saved (Guest No: {guest_number})")
            
            # Safe Firebase sync
            try:
                sync_guest_to_firebase(
                    guest_info['name'], 
                    guest_info['plate_number'], 
                    guest_info['office']
                )
                log_success("Guest synced to Firebase")
            except Exception as e:
                log_warning(f"Firebase sync failed: {e}")
            
            return True
        else:
            log_error("Failed to save guest record")
            return False
    except Exception as e:
        log_error(f"Error storing guest in database: {e}")
        return False
