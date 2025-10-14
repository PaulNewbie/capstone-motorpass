# etc/utils/verification_helpers.py
"""
Helper functions for verification flow to reduce code duplication in student.py
Maintains exact same flow and behavior, just organized better
"""

import time
import os
from etc.services.hardware.led_control import set_led_idle, set_led_success
from etc.services.hardware.buzzer_control import play_success
from etc.utils.led_helpers import execute_failure_feedback_concurrent


# ============= LOGGING HELPERS =============

def log_step(message, emoji="ℹ️"):
    """Standardized logging with emoji"""
    print(f"{emoji} {message}")

def log_success(message):
    """Log success message"""
    print(f"✅ {message}")

def log_error(message):
    """Log error message"""
    print(f"❌ {message}")

def log_warning(message):
    """Log warning message"""
    print(f"⚠️ {message}")

def log_info(message):
    """Log info message"""
    print(f"📋 {message}")

def log_cleanup(message):
    """Log cleanup action"""
    print(f"🗑️ {message}")


# ============= IMAGE CLEANUP HELPERS =============

def cleanup_image_file(image_path):
    """
    Safely clean up image file with error handling
    Returns True if successful, False otherwise
    """
    if not image_path:
        return False
        
    try:
        if os.path.exists(image_path):
            os.remove(image_path)
            log_cleanup(f"Cleaned up image file: {os.path.basename(image_path)}")
            return True
    except Exception as e:
        log_warning(f"Could not clean up image: {e}")
    return False


# ============= FEEDBACK HELPERS =============

def handle_verification_failure(status_callback, reason, cleanup_image_path=None):
    """
    Handle verification failure with consistent feedback and cleanup
    
    Args:
        status_callback: GUI callback function
        reason: Failure reason string
        cleanup_image_path: Optional image path to clean up
    
    Returns:
        dict: Failure result with standard format
    """
    log_error(f"Verification failed: {reason}")
    
    result_data = {'verified': False, 'reason': reason}
    execute_failure_feedback_concurrent(status_callback, result_data)
    time.sleep(3.0)
    
    # Clean up image if provided
    if cleanup_image_path:
        cleanup_image_file(cleanup_image_path)
    
    set_led_idle()
    return result_data


def handle_time_in_success(status_callback, message=None, duration=5.0):
    """
    Handle successful TIME IN with feedback
    
    Args:
        status_callback: GUI callback function
        message: Optional custom success message
        duration: LED success duration in seconds
    
    Returns:
        str: Timestamp of the TIME IN
    """
    timestamp = time.strftime('%H:%M:%S')
    
    if not message:
        message = f'✅ TIME IN recorded at {timestamp}'
    
    log_success(message)
    status_callback({'current_step': message})
    
    set_led_success(duration=duration)
    play_success()
    
    return timestamp


def handle_time_in_failure(status_callback, cleanup_image_path=None):
    """
    Handle failed TIME IN recording
    
    Args:
        status_callback: GUI callback function
        cleanup_image_path: Optional image path to clean up
    
    Returns:
        dict: Failure result
    """
    status_callback({'current_step': '❌ Failed to record TIME IN'})
    return handle_verification_failure(
        status_callback,
        'Failed to record TIME IN',
        cleanup_image_path
    )
    
def handle_license_capture_cancelled(status_callback):
    """Handle when user cancels license capture"""
    print("🛑 User cancelled license capture")
    status_callback({'current_step': '❌ License capture cancelled'})
    return handle_verification_failure(status_callback, 'User cancelled')

def handle_license_capture_error(status_callback, reason="Unknown error"):
    """Handle generic license capture errors"""
    print(f"❌ License capture failed: {reason}")
    status_callback({'current_step': '❌ License capture failed'})
    return handle_verification_failure(status_callback, 'License capture failed')


# ============= MANUAL INPUT HELPERS =============

def log_manual_input_cancelled(attempt_number):
    """Log cancelled manual input attempt"""
    log_error(f"Manual input attempt {attempt_number} cancelled")


def handle_manual_override_failure(status_callback, cleanup_image_path=None):
    """
    Handle failed manual override after all attempts
    
    Args:
        status_callback: GUI callback function
        cleanup_image_path: Optional image path to clean up
    
    Returns:
        dict: Failure result
    """
    log_error("Manual override DENIED - Both attempts failed")
    return handle_verification_failure(
        status_callback,
        'Manual override failed',
        cleanup_image_path
    )


# ============= VERIFICATION STATUS HELPERS =============

def handle_student_permit_denied(status_callback, cleanup_image_path=None):
    """
    Handle Student Permit detection (not allowed)
    
    Args:
        status_callback: GUI callback function
        cleanup_image_path: Optional image path to clean up
    
    Returns:
        dict: Failure result
    """
    status_callback({'current_step': '❌ Student Permit detected - Access denied'})
    return handle_verification_failure(
        status_callback,
        'Student Permit not allowed',
        cleanup_image_path
    )


def handle_student_license_denied(status_callback, cleanup_image_path=None):
    """
    Handle Student Driver License detection (not allowed)
    
    Args:
        status_callback: GUI callback function
        cleanup_image_path: Optional image path to clean up
    
    Returns:
        dict: Failure result
    """
    log_error("Student Driver License likely detected in camera preview")
    status_callback({'current_step': '❌ Student Driver License not allowed - Access denied'})
    return handle_verification_failure(
        status_callback,
        'Student Driver License not allowed',
        cleanup_image_path
    )


def handle_expired_license(status_callback, user_info, days_overdue):
    """
    Handle expired license with feedback
    
    Args:
        status_callback: GUI callback function
        user_info: User information dictionary
        days_overdue: Number of days license is overdue
    
    Returns:
        dict: Failure result
    """
    log_warning(f"License expired {days_overdue} days ago")
    status_callback({
        'current_step': f'⚠️ License expired {days_overdue} days ago - Access denied'
    })
    
    result_data = {'verified': False, 'reason': 'License has expired'}
    execute_failure_feedback_concurrent(status_callback, result_data)
    time.sleep(5.0)
    
    set_led_idle()
    return result_data


# ============= VERIFICATION RESULT BUILDERS =============

def build_standard_success_result(user_info, timestamp, time_action='IN', guest_info_input=None):
    """
    Build standard success result dictionary for both students and guests.

    Args:
        user_info: dict - basic user or guest info
        timestamp: str - time string (e.g., '08:01:28')
        time_action: str - 'IN' or 'OUT'
        guest_info_input: dict (optional) - only used for guest workflows

    Returns:
        dict: Standardized result for both students and guests
    """
    # Fallback to user_info if guest_info_input is not provided
    info_source = guest_info_input or user_info

    return {
        'verified': True,
        'name': user_info.get('name', 'N/A'),
        'student_id': user_info.get('student_id', user_info.get('unified_id', 'N/A')),
        'user_type': user_info.get('user_type', 'STUDENT'),
        'time_action': time_action,
        'timestamp': timestamp,
        'plate_number': info_source.get('plate_number', 'N/A'),
        'office': info_source.get('office', 'N/A'),
    }




def build_manual_override_result(user_info, timestamp):
    """
    Build manual override success result
    
    Args:
        user_info: User information dictionary
        timestamp: Time of verification
    
    Returns:
        dict: Manual override success result
    """
    result = build_standard_success_result(user_info, timestamp, 'IN')
    result['manual_override'] = True
    return result


# ============= VERIFICATION SUMMARY HELPERS =============

def create_verification_summary(helmet=True, fingerprint=True, 
                               license_valid=True, license_detected=True, 
                               name_match=True):
    """
    Create standardized verification summary dictionary
    
    Args:
        helmet: Helmet verification status
        fingerprint: Fingerprint verification status
        license_valid: License expiration validity
        license_detected: License detection status
        name_match: Name matching status
    
    Returns:
        dict: Verification summary
    """
    return {
        'helmet': helmet,
        'fingerprint': fingerprint,
        'license_valid': license_valid,
        'license_detected': license_detected,
        'name_match': name_match
    }


# ============= MANUAL INPUT WORKFLOW =============

def process_manual_input_workflow(status_callback, user_info, actual_license_name, 
                                 attempt_number, get_manual_input_func):
    """
    Process manual input workflow for license verification
    Handles both attempts with proper error handling
    """
    log_warning(f"Starting manual input workflow - Attempt {attempt_number}")
    
    # Call with correct signature
    manual_input = get_manual_input_func(
        user_info.get('name', 'N/A'),
        actual_license_name or "Unknown",
        status_callback,
        attempt_number
    )
    
    # Check if cancelled
    if manual_input is None:
        log_manual_input_cancelled(attempt_number)
        return False, None
    
    # Normalize both names for comparison (remove extra spaces, lowercase)
    def normalize_name(name):
        """Remove extra spaces and normalize for comparison"""
        import re
        # Replace multiple spaces with single space, strip, lowercase
        normalized = re.sub(r'\s+', ' ', name.strip()).lower()
        return normalized
    
    user_input_normalized = normalize_name(manual_input)
    expected_name_normalized = normalize_name(user_info.get('name', ''))
    
    # Compare normalized names
    if user_input_normalized == expected_name_normalized:
        log_success(f"Manual override GRANTED - Attempt {attempt_number}")
        
        # Build success result
        import time
        timestamp = time.strftime('%H:%M:%S')
        manual_result = build_manual_override_result(user_info, timestamp)
        
        return True, manual_result
    else:
        log_error(f"Manual override DENIED - Name mismatch on attempt {attempt_number}")
        print(f"   ❌ Input: '{user_input_normalized}'")
        print(f"   ❌ Expected: '{expected_name_normalized}'")
        return False, None
