import threading
import time

from etc.services.hardware.led_control import *  
from etc.services.hardware.buzzer_control import *

def execute_failure_feedback_concurrent(status_callback, result_data):
    """
    Execute buzzer, LED, and GUI feedback concurrently for failures.
    All three will start at the same time and run in parallel.
    """
    buzzer_duration = 3.0
    led_duration = 5.0
    gui_duration = 5.0
    
    buzzer_thread = threading.Thread(target=play_failure, daemon=True)
    led_thread = threading.Thread(target=set_led_failed_fast_blink, daemon=True)
    gui_thread = threading.Thread(
        target=lambda: status_callback({'final_result': result_data}),
        daemon=True
    )
    
    print("🚨 Starting concurrent failure feedback...")
    start_time = time.time()
    
    buzzer_thread.start()
    led_thread.start()
    gui_thread.start()
    
    buzzer_thread.join(timeout=buzzer_duration)
    led_thread.join(timeout=led_duration)
    gui_thread.join(timeout=gui_duration)
    
    elapsed = time.time() - start_time
    print(f"✅ All feedback completed in {elapsed:.2f}s")

def execute_success_feedback_concurrent(status_callback, result_data, duration=5.0):
    """
    Execute buzzer, LED, and GUI feedback concurrently for success.
    """
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
    
    buzzer_thread.start()
    led_thread.start()
    gui_thread.start()
    
    buzzer_thread.join(timeout=3.0)
    led_thread.join(timeout=duration)
    gui_thread.join(timeout=duration)
    
    elapsed = time.time() - start_time
    print(f"✅ All feedback completed in {elapsed:.2f}s")
