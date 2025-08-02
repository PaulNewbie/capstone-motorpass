# controllers/vip.py - Complete VIP Controller

from database.vip_operations import (
    record_vip_time_in, 
    record_vip_time_out, 
    check_vip_status
)

def authenticate_admin_for_vip():
    """Authenticate admin fingerprint for VIP access"""
    try:
        from controllers.admin import authenticate_admin
        
        print("\n🔐 ADMIN AUTHENTICATION REQUIRED FOR VIP ACCESS")
        print("Please place finger on sensor...")
        
        return authenticate_admin()
    except Exception as e:
        print(f"❌ VIP Authentication error: {e}")
        return False

def determine_vip_action(plate_number):
    """Determine if plate number should TIME IN or TIME OUT"""
    try:
        if not plate_number or not plate_number.strip():
            return {
                'action': None,
                'message': "Plate number is required!"
            }
        
        plate_number = plate_number.strip().upper()
        
        # Check if VIP is currently IN
        vip_status = check_vip_status(plate_number)
        
        if vip_status['found']:
            # EXISTS in currently-in list → TIME OUT
            return {
                'action': 'TIME_OUT',
                'message': f"VIP {plate_number} is currently IN - will TIME OUT",
                'vip_info': vip_status
            }
        else:
            # NOT EXISTS in currently-in list → TIME IN
            return {
                'action': 'TIME_IN',
                'message': f"VIP {plate_number} not found - will TIME IN"
            }
        
    except Exception as e:
        return {
            'action': None,
            'message': f"Error: {str(e)}"
        }

def process_vip_time_in(plate_number, purpose):
    """Simple TIME IN process with purpose"""
    try:
        if not purpose or purpose.strip() == "":
            return {
                'success': False,
                'message': "Purpose is required for TIME IN!"
            }
        
        result = record_vip_time_in(plate_number, purpose)
        
        if result['success']:
            print(f"✅ VIP TIME IN: {plate_number} - {purpose}")
        else:
            print(f"❌ VIP TIME IN failed: {result['message']}")
        
        return result
        
    except Exception as e:
        return {
            'success': False,
            'message': f"TIME IN error: {str(e)}"
        }

def process_vip_time_out(plate_number):
    """Simple TIME OUT process"""
    try:
        result = record_vip_time_out(plate_number)
        
        if result['success']:
            print(f"✅ VIP TIME OUT: {plate_number}")
        else:
            print(f"❌ VIP TIME OUT failed: {result['message']}")
        
        return result
        
    except Exception as e:
        return {
            'success': False,
            'message': f"TIME OUT error: {str(e)}"
        }

def validate_vip_plate_format(plate_number):
    """Validate plate number format (optional)"""
    try:
        if not plate_number:
            return False, "Plate number is required"
        
        plate_number = plate_number.strip().upper()
        
        # Basic validation - adjust according to your needs
        if len(plate_number) < 2:
            return False, "Plate number too short"
        
        if len(plate_number) > 15:
            return False, "Plate number too long"
        
        # You can add more specific validation rules here
        # For now, just check for basic alphanumeric
        if not all(c.isalnum() or c in ['-', ' '] for c in plate_number):
            return False, "Invalid characters in plate number"
        
        return True, "Valid"
        
    except Exception as e:
        return False, f"Validation error: {str(e)}"

def get_vip_purposes():
    """Get available VIP purposes"""
    return ["Official Visit", "Meeting", "Inspection", "Emergency"]
