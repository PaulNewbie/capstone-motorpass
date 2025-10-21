# main.py - FINAL FIX with a delay added to the restart process

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
from etc.services.hardware.buzzer_control import init_buzzer, cleanup_buzzer, play_ready
from etc.services.hardware.rpi_camera import force_camera_cleanup
from database.db_operations import initialize_all_databases

def initialize_system():
    """Initialize system components"""
    print(f" {SYSTEM_NAME} System Initialization")
    print("="*20)
    
    # Initialize LED system
    led_ok = init_led_system(red_pin=18, green_pin=16)
    print(f"💡 LED System: {'✅' if led_ok else '❌'}")
    
    buzzer_ok = init_buzzer()
    if buzzer_ok:
        play_ready() # Beep to confirm it's working
    print(f"🔊 Buzzer System: {'✅' if buzzer_ok else '❌'}")
    
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
        cleanup_buzzer()
    except:
        pass

def restart_application():
    """Restart the entire application with a delay"""
    print("\n🔄 Restarting...")
    
    # Clean up system resources
    cleanup_system()

    # time.sleep(10)

    script_path = os.path.abspath(__file__)
    subprocess.Popen([sys.executable, script_path])
    sys.exit(0)

def student_wrapper(main_window=None):
    """Simple wrapper - hide window, run process, then restart"""
    try:
        if main_window:
            main_window.withdraw()
        
        # This function now correctly manages its own GUI and cleanup
        student_verification()
        
    except Exception as e:
        print(f"❌ Error in student verification: {e}")
    finally:
        # The restart is now the very last thing that happens
        restart_application()

def guest_wrapper(main_window=None):
    """Simple wrapper - hide window, run process, then restart"""
    try:
        if main_window:
            main_window.withdraw()
        
        guest_verification()
        
    except Exception as e:
        print(f"❌ Error in guest verification: {e}")
    finally:
        restart_application()

def admin_wrapper(main_window=None):
    """Admin wrapper passes the main window to the admin panel"""
    try:
        admin_panel(main_window=main_window)
        
    except Exception as e:
        print(f"❌ Error in admin panel: {e}")
    finally:
        restart_application()

def main():
    """Main function"""
    try:
        print(f"\n{'='*60}")
        print(f"🚗 {SYSTEM_NAME} v{SYSTEM_VERSION}")
        print(f"{'='*60}")
        
        if not initialize_system():
            print("❌ System initialization failed!")
            return False
        
        main_gui = MotorPassGUI(
            system_name=SYSTEM_NAME,
            system_version=SYSTEM_VERSION,
            student_function=student_wrapper,
            guest_function=guest_wrapper,
            admin_function=admin_wrapper
        )
        
        main_gui.run()
        
    except KeyboardInterrupt:
        print("\n⚠️ System interrupted by user")
    except Exception as e:
        print(f"\n❌ System error: {e}")
    finally:
        # A final cleanup call when the entire application is truly exiting
        cleanup_system()

if __name__ == "__main__":
    main()
