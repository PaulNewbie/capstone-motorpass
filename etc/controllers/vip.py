# etc/controllers/vip.py - Complete VIP Controller with Guard Tracking
import re
from database.vip_operations import (
    record_vip_time_in, 
    record_vip_time_out, 
    check_vip_status,
    record_vip_time_in_with_guard,
    record_vip_time_out_with_guard
)

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

# NEW FUNCTIONS WITH GUARD TRACKING

def process_vip_time_in_with_guard(plate_number, purpose, guard_info):
    """Process VIP TIME IN with guard fingerprint information"""
    try:
        if not purpose or purpose.strip() == "":
            return {
                'success': False,
                'message': "Purpose is required for TIME IN!"
            }
        
        if not guard_info or not guard_info.get('name'):
            return {
                'success': False,
                'message': "Guard information is required!"
            }
        
        result = record_vip_time_in_with_guard(plate_number, purpose, guard_info)
        
        if result['success']:
            print(f"✅ VIP TIME IN: {plate_number} - {purpose} (Guard: {guard_info['name']})")
        else:
            print(f"❌ VIP TIME IN failed: {result['message']}")
        
        return result
        
    except Exception as e:
        return {
            'success': False,
            'message': f"TIME IN error: {str(e)}"
        }

def process_vip_time_out_with_guard(plate_number, guard_info):
    """Process VIP TIME OUT with guard fingerprint information"""
    try:
        if not guard_info or not guard_info.get('name'):
            return {
                'success': False,
                'message': "Guard information is required!"
            }
        
        result = record_vip_time_out_with_guard(plate_number, guard_info)
        
        if result['success']:
            print(f"✅ VIP TIME OUT: {plate_number} (Guard: {guard_info['name']})")
        else:
            print(f"❌ VIP TIME OUT failed: {result['message']}")
        
        return result
        
    except Exception as e:
        return {
            'success': False,
            'message': f"TIME OUT error: {str(e)}"
        }

def validate_vip_plate_format(plate_number):
    """Validate Philippine plate number formats including VIP, special, and temporary series."""
    try:
        if not plate_number:
            return False, "Plate number is required"

        plate_number = plate_number.strip().upper()

        # === 1️⃣ Basic sanity checks ===
        if len(plate_number) < 1:
            return False, "Input Plate No."
        if len(plate_number) > 17:
            return False, "Plate number too long"
        if not all(c.isalnum() or c in ['-', ' '] for c in plate_number):
            return False, "Invalid characters in plate number"

        # === 2️⃣ Known special / VIP plates ===
        special_plates = {
            "1": "President",
            "2": "Vice President",
            "3": "Senate President",
            "4": "Speaker of the House",
            "5": "Chief Justice",
            "SENATOR": "Senator",
            "PRESIDENT": "Office of the President",
            "VICE": "Vice President",
            "DIPLOMAT": "Diplomatic Plate",
            "CONSUL": "Honorary Consul",
            "GOV": "Governor",
            "MAYOR": "Mayor",
            "AMBASSADOR": "Ambassador",
        }

        if plate_number in special_plates:
            return True, f"Special Plate: {special_plates[plate_number]}"

        # === 3️⃣ Reject single-letter plates (e.g. "A") ===
        if re.match(r'^[A-Z]$', plate_number):
            return False, "Single-letter plates are not allowed"

        # === 4️⃣ Allow known Philippine formats (including temporary) ===
        valid_patterns = [
            r'^[A-Z]{3}[-\s]?\d{3}$',    # Old: ABC-123
            r'^[A-Z]{3}[-\s]?\d{4}$',    # New: ABC-1234
            r'^\d{4}[-\s]?[A-Z]{2}$',    # Motorcycle: 1234-AB
            r'^[A-Z]{2,7}$',             # Vanity: AA, CARL, VIPCAR, etc. (no single-letter)
            r'^[A-Z0-9]{2,8}$',          # Alternate alphanumeric: 1A2B3C, etc.
            r'^\d{4,20}$',               # Temporary numeric-only: 130100012345678
        ]

        for pattern in valid_patterns:
            if re.match(pattern, plate_number):
                return True, "Valid standard, temporary, or vanity plate"

        # === 5️⃣ No match found ===
        return False, "Invalid plate format"

    except Exception as e:
        return False, f"Validation error: {str(e)}"
   
def get_vip_purposes():
    """Get available VIP purposes"""
    return ["Official Visit", "Meeting", "Inspection", "Emergency"]
