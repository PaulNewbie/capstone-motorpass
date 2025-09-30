# ui/business/student_operations.py - FIXED: Handle correct status keys from controller

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
        """Update GUI status - FIXED: Handle correct status keys from controller"""
        try:
            # FIXED: Handle helmet status with correct key names
            if 'helmet_status' in status_dict:
                status = status_dict['helmet_status']
                gui_instance.helmet_status.set(status)
            elif 'helmet_detected' in status_dict:
                # Legacy support for old key name
                if status_dict['helmet_detected']:
                    gui_instance.helmet_status.set("VERIFIED")
                else:
                    gui_instance.helmet_status.set("FAILED")
            
            # FIXED: Handle fingerprint status with correct key names
            if 'fingerprint_status' in status_dict:
                status = status_dict['fingerprint_status']
                gui_instance.fingerprint_status.set(status)
            elif 'fingerprint_result' in status_dict:
                # Legacy support for old key name
                result = status_dict['fingerprint_result']
                if result.get('verified', False):
                    gui_instance.fingerprint_status.set("VERIFIED")
                    user_info = result.get('user_info', {})
                    if user_info:
                        gui_instance.show_user_info(user_info)
                else:
                    gui_instance.fingerprint_status.set("FAILED")
            
            # FIXED: Handle license status with correct key names
            if 'license_status' in status_dict:
                status = status_dict['license_status']
                gui_instance.license_status.set(status)
            elif 'license_verified' in status_dict:
                # Legacy support for old key name
                if status_dict['license_verified']:
                    gui_instance.license_status.set("VERIFIED")
                else:
                    gui_instance.license_status.set("FAILED")
            
            # Handle user info display
            if 'user_info' in status_dict:
                user_info = status_dict['user_info']
                if user_info:
                    gui_instance.show_user_info(user_info)
            
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
        
    def update_fingerprint(self, verified, user_info=None):
        """Update fingerprint status"""
        self.fingerprint_verified = verified
        if user_info:
            self.user_info = user_info
            
    def update_license(self, verified):
        """Update license status"""
        self.license_verified = verified
        
    def is_complete(self):
        """Check if all verifications are complete"""
        return self.helmet_verified and self.fingerprint_verified and self.license_verified
        
    def get_summary(self):
        """Get verification summary"""
        return {
            'helmet': self.helmet_verified,
            'fingerprint': self.fingerprint_verified,
            'license': self.license_verified,
            'user_info': self.user_info,
            'complete': self.is_complete()
        }
