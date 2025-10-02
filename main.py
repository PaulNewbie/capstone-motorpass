# main.py - Simple fix with cleanup calls added
import subprocess
import sys
import os
import time
from etc.ui.main_window import MotorPassGUI

# Import controllers
from etc.controllers.admin import admin_panel
from etc.controllers.student import student_verification
from etc.controllers.guest import guest_verification

# Import configuration
from config import SYSTEM_NAME, SYSTEM_VERSION

# Import services
from etc.services.hardware.led_control import (
    init_led_system, 
    set_led_idle, 
    cleanup_led_system
)
from etc.services.hardware.rpi_camera import force_camera_cleanup
from database.db_operations import initialize_all_databases

def initialize_system():
    """Initialize system components"""
    print(f"🚗 {SYSTEM_NAME} System Initialization")
    print("="*50)
    
    # Initialize LED system
    led_ok = init_led_system(red_pin=18, green_pin=16)
    print(f"💡 LED System: {'✅' if led_ok else '❌'}")
    
    # Initialize all databases
    db_ok = initialize_all_databases()
    
    if not db_ok:
        print("⚠️ Some databases failed to initialize, but system will continue")
    
    print("✅ System ready!")
    set_led_idle()
    return True

def cleanup_system():
    """Cleanup system resources"""
    try:
        cleanup_led_system()
        force_camera_cleanup()
    except:
        pass

def restart_application():
    """Restart the entire application"""
    print("\n🔄 Restarting...")
    
    # Clean up and restart
    cleanup_system()
    time.sleep(0.5)
    
    script_path = os.path.abspath(__file__)
    subprocess.Popen([sys.executable, script_path])
    sys.exit(0)

def student_wrapper(main_window=None):
    """Simple wrapper - hide window, run process, then restart"""
    try:
        if main_window:
            main_window.withdraw()  # Hide main window for student
        
        result = student_verification()  # Run your original function
        
        # Only restart after verification completes successfully
        restart_application()
        return result
        
    except Exception as e:
        print(f"❌ Error in student verification: {e}")
        # Only restart on error if needed
        restart_application()
        raise

def guest_wrapper(main_window=None):
    """Simple wrapper - hide window, run process, then restart"""
    try:
        if main_window:
            main_window.withdraw()  # Hide main window for guest
        
        result = guest_verification()  # Run your original function
        
        # Only restart after verification completes
        restart_application()
        return result
        
    except Exception as e:
        print(f"❌ Error in guest verification: {e}")
        restart_application()
        raise

def admin_wrapper(main_window=None):
    """FIXED: Don't hide main window - let admin authentication handle it"""
    try:
        # DON'T hide main_window here - pass it to admin_panel instead
        result = admin_panel(main_window=main_window)
        
        # Only restart after admin completes
        restart_application()
        return result
        
    except Exception as e:
        print(f"❌ Error in admin panel: {e}")
        restart_application()
        raise

def main():
    """Main function - unchanged except using wrappers"""
    try:
        print(f"\n{'='*60}")
        print(f"🚗 {SYSTEM_NAME} v{SYSTEM_VERSION}")
        print(f"{'='*60}")
        
        # Initialize system
        if not initialize_system():
            print("❌ System initialization failed!")
            return False
        
        # Create main GUI with wrapper functions (instead of original functions)
        main_gui = MotorPassGUI(
            system_name=SYSTEM_NAME,
            system_version=SYSTEM_VERSION,
            student_function=student_wrapper,  # Use wrapper
            guest_function=guest_wrapper,      # Use wrapper
            admin_function=admin_wrapper       # Use wrapper
        )
        
        # Run main GUI
        main_gui.run()
        
    except KeyboardInterrupt:
        print("\n⚠️ System interrupted by user")
        cleanup_system()
        return False
    except Exception as e:
        print(f"\n❌ System error: {e}")
        cleanup_system()
        return False
    finally:
        cleanup_system()

if __name__ == "__main__":
    main()
