# ui/business/student_operations.py - ONLY business logic, no UI duplication

import threading
from datetime import datetime

class StudentVerificationManager:
    """Manages student verification business logic - NO UI code"""
    
    def __init__(self):
        self.verification_in_progress = False
        
    def start_verification(self, verification_function, callback):
        """Start verification in background thread"""
        def run_verification():
            try:
                self.verification_in_progress = True
                result = verification_function(callback=callback)
                callback({'final_result': result})
            except Exception as e:
                error_result = {
                    'verified': False,
                    'reason': f'Error: {str(e)}'
                }
                callback({'final_result': error_result})
            finally:
                self.verification_in_progress = False

        verification_thread = threading.Thread(target=run_verification, daemon=True)
        verification_thread.start()
    
    def update_status(self, status_dict, gui_instance):
        """Update GUI status - delegates UI updates to GUI"""
        try:
            # Handle fingerprint result with user info
            if 'fingerprint_result' in status_dict:
                result = status_dict['fingerprint_result']
                if result.get('verified', False):
                    gui_instance.fingerprint_status.set("VERIFIED")
                    user_info = result.get('user_info', {})
                    if user_info:
                        gui_instance.show_user_info(user_info)
                else:
                    gui_instance.fingerprint_status.set("FAILED")
            
            # Handle helmet status
            if 'helmet_detected' in status_dict:
                if status_dict['helmet_detected']:
                    gui_instance.helmet_status.set("VERIFIED")
                else:
                    gui_instance.helmet_status.set("FAILED")
            
            # Handle license status
            if 'license_verified' in status_dict:
                if status_dict['license_verified']:
                    gui_instance.license_status.set("VERIFIED")
                else:
                    gui_instance.license_status.set("FAILED")
            
            # Handle current step updates
            if 'current_step' in status_dict:
                gui_instance.current_step.set(status_dict['current_step'])
            
            # Handle final result
            if 'final_result' in status_dict:
                result = status_dict['final_result']
                print(f"\n{'='*60}")
                print(f"🏁 VERIFICATION COMPLETE")
                print(f"✅ Result: {'PASSED' if result.get('verified', False) else 'FAILED'}")
                if not result.get('verified', False):
                    print(f"❌ Reason: {result.get('reason', 'Unknown')}")
                print(f"{'='*60}")
                
                # Auto-close after showing result
                gui_instance.root.after(3000, gui_instance.close)
                
        except Exception as e:
            print(f"Error updating status: {e}")


class StudentStatusTracker:
    """Track verification status - pure data management"""
    
    def __init__(self):
        self.helmet_verified = False
        self.fingerprint_verified = False
        self.license_verified = False
        self.user_info = None
        
    def update_helmet(self, verified):
        """Update helmet status"""
        self.helmet_verified = verified
        return {'helmet_detected': verified}
    
    def update_fingerprint(self, verified, user_info=None):
        """Update fingerprint status"""
        self.fingerprint_verified = verified
        self.user_info = user_info
        return {
            'fingerprint_result': {
                'verified': verified,
                'user_info': user_info or {}
            }
        }
    
    def update_license(self, verified):
        """Update license status"""
        self.license_verified = verified
        return {'license_verified': verified}
    
    def is_complete(self):
        """Check if verification is complete"""
        return all([self.helmet_verified, self.fingerprint_verified, self.license_verified])
    
    def get_completion_percentage(self):
        """Get completion percentage"""
        completed = sum([self.helmet_verified, self.fingerprint_verified, self.license_verified])
        return int((completed / 3) * 100)


class StudentTimeManager:
    """Manage verification timing"""
    
    def __init__(self):
        self.start_time = None
        self.timeout_duration = 300  # 5 minutes
        
    def start_timer(self):
        """Start verification timer"""
        self.start_time = datetime.now()
        
    def get_elapsed_seconds(self):
        """Get elapsed time in seconds"""
        if not self.start_time:
            return 0
        return (datetime.now() - self.start_time).total_seconds()
    
    def is_timeout(self):
        """Check if timeout exceeded"""
        return self.get_elapsed_seconds() > self.timeout_duration
    
    def get_remaining_seconds(self):
        """Get remaining seconds before timeout"""
        return max(0, self.timeout_duration - self.get_elapsed_seconds())
