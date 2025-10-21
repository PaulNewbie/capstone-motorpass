# services/buzzer_control.py - Clean and Simple Buzzer Control with Config Check
import RPi.GPIO as GPIO
import time
import threading

# --- START OF FIX ---
# This code block helps Python find the 'config.py' file from the project root
import sys
import os

# Get the absolute path of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))
# Navigate three levels up to get to the project root (hardware -> services -> etc -> MotorPass)
project_root = os.path.abspath(os.path.join(script_dir, '..', '..', '..'))

# Add the project root to the Python path
if project_root not in sys.path:
    sys.path.insert(0, project_root)
# --- END OF FIX ---

from config import ENABLE_BUZZER

# Disable GPIO warnings
GPIO.setwarnings(False)

class BuzzerController:
    def __init__(self, buzzer_pin=22):
        self.buzzer_pin = buzzer_pin
        self.is_playing = False
        
        if not ENABLE_BUZZER:
            return
        
        # Clean up any existing GPIO setup
        try:
            GPIO.cleanup([self.buzzer_pin])
        except:
            pass
        
        # Setup GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.buzzer_pin, GPIO.OUT)
        GPIO.output(self.buzzer_pin, GPIO.LOW)
    
    def simple_beep(self, duration=0.2):
        """Simple clean beep - no PWM, just on/off"""
        if not ENABLE_BUZZER:
            return
        try:
            GPIO.output(self.buzzer_pin, GPIO.HIGH)
            time.sleep(duration)
            GPIO.output(self.buzzer_pin, GPIO.LOW)
        except Exception as e:
            print(f"⚠️ Buzzer error: {e}")
    
    def play_pattern(self, pattern_name):
        """Play simple patterns without threading complications"""
        if not ENABLE_BUZZER or self.is_playing:
            return
        
        self.is_playing = True
        
        try:
            if pattern_name == "processing":
                # Two quick beeps
                self.simple_beep(0.1)
                time.sleep(0.1)
                self.simple_beep(0.1)
                
            elif pattern_name == "success":
                # Three ascending beeps
                self.simple_beep(0.1)
                time.sleep(0.05)
                self.simple_beep(0.1)
                time.sleep(0.05)
                self.simple_beep(0.15)
                
            elif pattern_name == "failure":
                # OLD: One longer beep - NOT DISTINCTIVE ENOUGH
                # self.simple_beep(2)
                
                # NEW: SECURITY ALARM - Multiple rapid beeps to alert guards
                # Pattern: 3 sets of rapid beeps with pauses
                print("🚨 SECURITY ALARM: Authentication failed!")
                
                for alarm_cycle in range(2):  # 3 cycles
                    # Rapid beeps (SOS-style)
                    for beep in range(3):
                        self.simple_beep(0.15)  # Short beep
                        time.sleep(0.1)  # Quick gap
                    
                    # Longer beeps in middle of pattern
                    for beep in range(2):
                        self.simple_beep(0.3)  # Longer beep
                        time.sleep(0.15)
                    
                    # Final rapid beeps
                    for beep in range(3):
                        self.simple_beep(0.15)
                        time.sleep(0.1)
                    
                    # Pause between cycles (except last cycle)
                    if alarm_cycle < 1:
                        time.sleep(0.5)
                
                print("🚨 Alarm pattern complete")
                
        except Exception as e:
            print(f"⚠️ Pattern error: {e}")
        finally:
            self.is_playing = False
    
    def cleanup(self):
        """Clean up GPIO resources"""
        if not ENABLE_BUZZER:
            return
        try:
            GPIO.output(self.buzzer_pin, GPIO.LOW)
            GPIO.cleanup([self.buzzer_pin])
        except:
            pass

# Global buzzer controller instance
buzzer_controller = None

def init_buzzer(pin=22):
    """Initialize the buzzer controller"""
    if not ENABLE_BUZZER:
        return True
        
    global buzzer_controller
    try:
        if buzzer_controller:
            buzzer_controller.cleanup()
        
        buzzer_controller = BuzzerController(pin)
        
        # Test with simple beep
        buzzer_controller.simple_beep(0.1)
        
        print(f"✅ Buzzer initialized on pin {pin}")
        return True
    except Exception as e:
        print(f"❌ Buzzer init error: {e}")
        return False

# Simple functions - only the 3 you need
def play_processing():
    """Start/processing sound"""
    if ENABLE_BUZZER and buzzer_controller:
        buzzer_controller.play_pattern("processing")

def play_success():
    """Success sound"""
    if ENABLE_BUZZER and buzzer_controller:
        buzzer_controller.play_pattern("success")

def play_failure():
    """Failure/Security Alarm sound - NOW WITH ENHANCED ALARM PATTERN"""
    if ENABLE_BUZZER and buzzer_controller:
        buzzer_controller.play_pattern("failure")

# Aliases for convenience
def play_ready():
    """System ready - same as processing"""
    play_processing()

def cleanup_buzzer():
    """Clean up buzzer system resources"""
    if not ENABLE_BUZZER:
        return
    global buzzer_controller
    if buzzer_controller:
        buzzer_controller.cleanup()
        buzzer_controller = None

# Test function
if __name__ == "__main__":
    print("🔊 Enhanced Buzzer Test with Security Alarm")
    
    if init_buzzer():
        print("Testing sounds...")
        
        print("\n1. Processing...")
        play_processing()
        time.sleep(2)
        
        print("\n2. Success...")
        play_success()
        time.sleep(2)
        
        print("\n3. SECURITY ALARM (Enhanced Failure Pattern)...")
        print("   Listen for the distinctive alarm pattern!")
        play_failure()
        time.sleep(2)
        
        print("\n✅ Test complete!")
        cleanup_buzzer()
    else:
        print("❌ Buzzer test failed!")
