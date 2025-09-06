# controllers/guest.py - Fixed Firebase integration

from etc.services.license_reader import *
from etc.services.helmet_infer import verify_helmet
from etc.services.led_control import *  
from etc.services.buzzer_control import *
from etc.services.rpi_camera import force_camera_cleanup
from etc.utils.display_helpers import display_separator, display_verification_result
from etc.utils.gui_helpers import show_results_gui, get_guest_info_gui, updated_guest_office_gui
from etc.utils.timeout_security import timeout_security_verification
import difflib
import time

# FIXED: Import Firebase helper instead of direct import
from etc.utils.firebase_helper import sync_guest_to_firebase, sync_time_to_firebase, check_firebase_status

from database.db_operations import (
    add_guest,  # Keep your existing function
    get_guest_time_status,
    get_guest_from_database,
    create_guest_time_data, 
    process_guest_time_in,
    process_guest_time_out
)

def guest_verification():
    """Main guest verification with GUI"""
    print("\n🎫 GUEST VERIFICATION")
    print("🖥️ Opening GUI interface...")
    
    # Import GUI here to avoid circular imports
    from etc.ui.guest_gui import GuestVerificationGUI
    
    # No cleanup needed at start
    
    # Create and run GUI
    gui = GuestVerificationGUI(run_guest_verification_with_gui)
    gui.run()

def run_guest_verification_with_gui(status_callback):
    """Simple guest verification - automatic timeout if found in system"""
    
    # Initialize systems
    init_buzzer()
    set_led_processing()
    play_processing()
    
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
        
        # Step 2: License capture with retake loop for new guests only
        while True:
            # License capture
            status_callback({'current_step': '📄 Capturing license... (Check terminal for camera)'})
            status_callback({'license_status': 'PROCESSING'})
            
            print("\n" + "="*60)
            print("📄 LICENSE CAPTURE (Terminal Camera)")
            print("="*60)
            
            image_path = auto_capture_license_rpi()
            
            if not image_path:
                status_callback({'license_status': 'FAILED'})
                status_callback({'current_step': '❌ License capture failed'})
                set_led_idle()
                play_failure()
                cleanup_buzzer()
                return {'verified': False, 'reason': 'License capture failed'}
            
            status_callback({'license_status': 'DETECTED'})
            
            # Step 3: Extract name and check guest status
            status_callback({'current_step': '🔍 Processing license information...'})
            
            # Student Permit check
            try:
                ocr_preview = extract_text_from_image(image_path)
            except ValueError as e:
                if "STUDENT_PERMIT_DETECTED" in str(e):
                    print("❌ Student Permit detected - Access denied")
                    status_callback({'current_step': '❌ Student Permit not allowed - Access denied'})
                    safe_delete_temp_file(image_path)
                    set_led_idle()
                    play_failure()
                    cleanup_buzzer()
                    return {'verified': False, 'reason': 'Student Permit not allowed'}
                else:
                    raise e
            
            # Extract name using simple method
            ocr_lines = [line.strip() for line in ocr_preview.splitlines() if line.strip()]
            detected_name = extract_guest_name_from_license(ocr_lines)
            
            print(f"📄 Detected name: {detected_name}")
            
            # Check guest status - LENIENT MATCHING
            current_status, guest_info = get_guest_time_status(detected_name)
            
            if current_status == 'IN':
                # AUTOMATIC TIMEOUT - No license verification needed!
                print(f"🔍 Found guest '{guest_info['name']}' currently IN")
                print(f"📄 Detected name: '{detected_name}'")
                print(f"🤔 Match confidence: {guest_info.get('similarity_score', 0)*100:.1f}%")
                
                status_callback({
                    'guest_info': {
                        'name': guest_info['name'],
                        'guest_number': guest_info['guest_number'],
                        'plate_number': guest_info['plate_number'],
                        'office': guest_info['office'],
                        'status': 'GUEST TIMEOUT - SECURITY CHECK'
                    }
                })
                
                status_callback({'current_step': '🔐 Security verification required for timeout...'})
                
                # Security verification only
                security_verified = timeout_security_verification(guest_info)
                
                if security_verified:
                    print("✅ Security code verified - proceeding with TIME OUT")
                    status_callback({'current_step': '🔍 Processing timeout...'})
                    
                    # NO LICENSE VERIFICATION - Direct timeout
                    time_result = process_guest_time_out(guest_info)
                    
                    if time_result['success']:
                        timestamp = time.strftime('%H:%M:%S')
                        status_callback({'current_step': f'✅ TIME OUT recorded at {timestamp}'})
                        set_led_success(duration=5.0)
                        play_success()
                        
                        status_callback({
                            'verification_summary': {
                                'helmet': True,
                                'license': True  # Always true for timeouts
                            }
                        })
                        
                        cleanup_buzzer()
                        safe_delete_temp_file(image_path)
                        return {
                            'verified': True,
                            'name': guest_info['name'],
                            'time_action': 'OUT',
                            'timestamp': timestamp,
                            'guest_number': guest_info['guest_number']
                        }
                    else:
                        status_callback({'current_step': '❌ Failed to record TIME OUT'})
                        set_led_idle()
                        play_failure()
                        cleanup_buzzer()
                        safe_delete_temp_file(image_path)
                        return {'verified': False, 'reason': 'Failed to record TIME OUT'}
                
                else:
                    # Security verification failed
                    print("❌ Security verification failed or cancelled")
                    status_callback({'current_step': '❌ Security verification failed - Timeout DENIED'})
                    safe_delete_temp_file(image_path)
                    set_led_idle()
                    play_failure()
                    cleanup_buzzer()
                    return {'verified': False, 'reason': 'Security verification failed'}
            
            else:
                # NEW GUEST TIME IN
                status_callback({
                    'guest_info': {
                        'name': detected_name if detected_name != "Guest" else "New Guest",
                        'status': 'NEW GUEST - REGISTRATION'
                    }
                })
                
                status_callback({'current_step': '🔍 Please provide guest information...'})
                
                # Get guest info with retake functionality
                guest_info_input = get_guest_info_gui(detected_name)
                
                # Handle different return values
                if guest_info_input == 'retake':
                    # User wants to retake license
                    print("📷 User requested license retake from registration form")
                    status_callback({'current_step': '📄 Retaking license scan...'})
                    safe_delete_temp_file(image_path)
                    continue  # Go back to license capture
                    
                elif not guest_info_input:
                    # User cancelled
                    status_callback({'current_step': '❌ Guest registration cancelled'})
                    safe_delete_temp_file(image_path)
                    set_led_idle()
                    play_failure()
                    cleanup_buzzer()
                    return {'verified': False, 'reason': 'Guest registration cancelled'}
                
                # Valid guest info provided - process time in
                status_callback({
                    'guest_info': {
                        'name': guest_info_input['name'],
                        'plate_number': guest_info_input['plate_number'],
                        'office': guest_info_input['office'],
                        'status': 'NEW GUEST - PROCESSING'
                    }
                })
                
                status_callback({'current_step': '🔍 Processing guest time in...'})
                
                # Simple license check for new guests
                guest_data_for_license = {
                    'name': guest_info_input['name'],
                    'plate_number': guest_info_input['plate_number'],
                    'office': guest_info_input['office'],
                    'is_guest': True
                }
                
                # Basic license verification
                try:
                    is_guest_verified = complete_guest_verification_flow(
                        image_path=image_path,
                        guest_info=guest_data_for_license,
                        helmet_verified=True
                    )
                except ValueError as e:
                    if "STUDENT_PERMIT_DETECTED" in str(e):
                        status_callback({'current_step': '❌ Student Permit detected - Access denied'})
                        set_led_idle()
                        play_failure()
                        cleanup_buzzer()
                        safe_delete_temp_file(image_path)
                        return {'verified': False, 'reason': 'Student Permit not allowed'}
                    else:
                        raise e
                
                if is_guest_verified:
                    # Store guest and process time in
                    store_guest_in_database(guest_info_input)
                    time_result = process_guest_time_in(guest_info_input)
                    
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
                        safe_delete_temp_file(image_path)
                        return {
                            'verified': True,
                            'name': guest_info_input['name'],
                            'time_action': 'IN',
                            'timestamp': timestamp,
                            'office': guest_info_input['office']
                        }
                    else:
                        status_callback({'current_step': '❌ Failed to record TIME IN'})
                        set_led_idle()
                        play_failure()
                        cleanup_buzzer()
                        safe_delete_temp_file(image_path)
                        return {'verified': False, 'reason': 'Failed to record TIME IN'}
                else:
                    status_callback({'current_step': '❌ Guest verification failed'})
                    set_led_idle()
                    play_failure()
                    cleanup_buzzer()
                    safe_delete_temp_file(image_path)
                    return {'verified': False, 'reason': 'License verification failed'}
        
    except Exception as e:
        print(f"❌ Error during verification: {e}")
        set_led_idle()
        play_failure()
        cleanup_buzzer()
        return {'verified': False, 'reason': str(e)}
                      
def store_guest_in_database(guest_info):
    """FIXED: Store guest with safe Firebase sync"""
    try:
        guest_data = {
            'full_name': guest_info['name'],
            'plate_number': guest_info['plate_number'],
            'office_visiting': guest_info['office']
        }
        
        # Your existing local database save
        guest_number = add_guest(guest_data)  # Keep your existing function
        
        if guest_number:
            print(f"✅ Guest record saved (Guest No: {guest_number})")
            
            # FIXED: Safe Firebase sync
            try:
                sync_guest_to_firebase(
                    guest_info['name'], 
                    guest_info['plate_number'], 
                    guest_info['office']
                )
                print("🔥 Guest synced to Firebase")
            except Exception as e:
                print(f"⚠️  Firebase sync failed: {e}")
            
            return True
        else:
            print(f"❌ Failed to save guest record")
            return False
    except Exception as e:
        print(f"❌ Error storing guest in database: {e}")
        return False

def check_firebase_sync_status():
    """FIXED: Check Firebase status safely"""
    try:
        status = check_firebase_status()
        if status:
            if status['online']:
                print("🔥 Firebase: CONNECTED ✅")
            else:
                print("📴 Firebase: OFFLINE ⚠️")
            return status
        else:
            print("⚠️  Firebase not available")
            return None
    except Exception as e:
        print(f"⚠️  Error checking Firebase: {e}")
        return None
