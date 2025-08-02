# controllers/vip.py - VIP Controller

from database.vip_operations import (
    record_vip_time_in, 
    record_vip_time_out, 
    check_vip_status,
    get_all_vip_records,
    get_vip_stats
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
        
        # Check if VIP is currently timed in
        vip_status = check_vip_status(plate_number)
        
        if vip_status['found']:
            # VIP exists and is IN -> TIME OUT
            return {
                'action': 'TIME_OUT',
                'message': f"VIP {plate_number} is currently IN - will TIME OUT",
                'vip_info': vip_status
            }
        else:
            # VIP not found or already OUT -> TIME IN
            return {
                'action': 'TIME_IN',
                'message': f"VIP {plate_number} not found - will TIME IN"
            }
        
    except Exception as e:
        print(f"❌ Error determining VIP action: {e}")
        return {
            'action': None,
            'message': f"Error: {str(e)}"
        }

def process_vip_time_in(plate_number, purpose):
    """Process VIP time in with validation"""
    try:
        # Validate inputs
        if not plate_number or not plate_number.strip():
            return {
                'success': False,
                'message': "Plate number is required!"
            }
        
        if not purpose or purpose not in ["Official Visit", "Meeting", "Inspection", "Emergency"]:
            return {
                'success': False,
                'message': "Valid purpose is required!"
            }
        
        # Clean plate number
        plate_number = plate_number.strip().upper()
        
        # Record to database
        result = record_vip_time_in(plate_number, purpose)
        
        if result['success']:
            print(f"✅ VIP Time In processed successfully: {plate_number}")
        else:
            print(f"❌ VIP Time In failed: {result['message']}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error processing VIP time in: {e}")
        return {
            'success': False,
            'message': f"Processing error: {str(e)}"
        }

def process_vip_time_out(plate_number):
    """Process VIP time out with validation"""
    try:
        # Validate input
        if not plate_number or not plate_number.strip():
            return {
                'success': False,
                'message': "Plate number is required!"
            }
        
        # Clean plate number
        plate_number = plate_number.strip().upper()
        
        # Record to database
        result = record_vip_time_out(plate_number)
        
        if result['success']:
            print(f"✅ VIP Time Out processed successfully: {plate_number}")
        else:
            print(f"❌ VIP Time Out failed: {result['message']}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error processing VIP time out: {e}")
        return {
            'success': False,
            'message': f"Processing error: {str(e)}"
        }

def get_vip_current_status(plate_number):
    """Get current VIP status"""
    try:
        if not plate_number or not plate_number.strip():
            return {'found': False, 'message': "Plate number is required"}
        
        plate_number = plate_number.strip().upper()
        return check_vip_status(plate_number)
        
    except Exception as e:
        print(f"❌ Error getting VIP status: {e}")
        return {'found': False, 'error': str(e)}

def get_vip_dashboard_data():
    """Get VIP dashboard data for admin panel"""
    try:
        stats = get_vip_stats()
        current_vips = get_all_vip_records(status='IN')
        
        return {
            'stats': stats,
            'current_vips': current_vips
        }
        
    except Exception as e:
        print(f"❌ Error getting VIP dashboard data: {e}")
        return {
            'stats': {'current_in': 0, 'today_visits': 0, 'total_records': 0},
            'current_vips': []
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
