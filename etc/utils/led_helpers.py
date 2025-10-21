# etc/utils/led_helpers.py
"""
Enhanced LED and Buzzer helper functions
Provides concurrent feedback execution for better user experience
"""

import threading
import time
from etc.services.hardware.led_control import *  
from etc.services.hardware.buzzer_control import *

def play_alarm_feedback():
    """
    Plays a fast red LED blink and the failure buzzer sound concurrently.
    This creates a synchronized audio-visual alarm for critical failures.
    """
    if not led_is_available():
        # If no LEDs, just play the sound
        play_failure()
        return

    # Create threads for LED and Buzzer so they run at the same time
    led_thread = threading.Thread(target=set_led_failed_fast_blink)
    buzzer_thread = threading.Thread(target=play_failure)

    # Start the threads
    led_thread.start()
    buzzer_thread.start()

    # Wait for both threads to complete
    led_thread.join()
    buzzer_thread.join()

def execute_failure_feedback_concurrent(status_callback, result_data):
    pass


def execute_success_feedback_concurrent(status_callback, result_data, duration=5.0):
    """
    Execute buzzer, LED, and GUI feedback concurrently for success.
    
    Args:
        status_callback: GUI callback function
        result_data: Dictionary with success information
        duration: How long to show success feedback
    """
    # Create threads for concurrent execution
    buzzer_thread = threading.Thread(target=play_success, daemon=True)
    led_thread = threading.Thread(
        target=lambda: set_led_success(duration=duration),
        daemon=True
    )
    gui_thread = threading.Thread(
        target=lambda: status_callback({'final_result': result_data}),
        daemon=True
    )
    
    print("✅ Starting concurrent success feedback...")
    start_time = time.time()
    
    # Start all threads simultaneously
    buzzer_thread.start()
    led_thread.start()
    gui_thread.start()
    
    # Wait for all threads to complete
    buzzer_thread.join(timeout=3.0)
    led_thread.join(timeout=duration)
    gui_thread.join(timeout=duration)
    
    elapsed = time.time() - start_time
    print(f"✅ All success feedback completed in {elapsed:.2f}s")


def quick_failure_feedback(status_callback, reason):
    """
    Quick failure feedback with shorter delay (1.5s instead of 3s)
    Useful for non-critical failures that don't need full alarm
    
    Args:
        status_callback: GUI callback function
        reason: Failure reason string
    """
    result_data = {'verified': False, 'reason': reason}
    execute_failure_feedback_concurrent(status_callback, result_data)
    time.sleep(1.5)  # Shorter delay
    set_led_idle()


def student_permit_denied_feedback(status_callback):
    """
    Specific feedback pattern for student permit detection
    
    Args:
        status_callback: GUI callback function
    """
    status_callback({'current_step': '❌ Student Permit detected - Access denied'})
    result_data = {'verified': False, 'reason': 'Student Permit not allowed'}
    execute_failure_feedback_concurrent(status_callback, result_data)
    time.sleep(3.0)
    set_led_idle()


def expired_license_feedback(status_callback, days_overdue):
    """
    Specific feedback for expired license with day count
    
    Args:
        status_callback: GUI callback function
        days_overdue: Number of days the license is overdue
    """
    status_callback({
        'current_step': f'⚠️ License expired {days_overdue} days ago - Access denied'
    })
    result_data = {'verified': False, 'reason': 'License has expired'}
    execute_failure_feedback_concurrent(status_callback, result_data)
    time.sleep(5.0)  # Longer delay for expired license
    set_led_idle()


def simple_led_buzzer_success(duration=5.0):
    """
    Simple success feedback without GUI callback
    Just LED and buzzer
    
    Args:
        duration: How long to show success LED
    """
    set_led_success(duration=duration)
    play_success()


def simple_led_buzzer_failure():
    """
    Simple failure feedback without GUI callback
    Just LED and buzzer
    """
    play_failure()
    set_led_failed_fast_blink()
    time.sleep(3.0)
    set_led_idle()
