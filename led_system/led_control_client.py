#!/usr/bin/env python3
"""
MotorPass LED Client - No Sudo Required
Drop-in replacement for your current led_control.py
Communicates with LED daemon via Unix socket
"""

import socket
import json
import time
import threading
from enum import Enum

class LEDState(Enum):
    """LED States"""
    IDLE = "idle"
    PROCESSING = "processing" 
    SUCCESS = "success"
    FAILED = "failed"
    OFF = "off"
    CAMERA = "camera"

class LEDClient:
    """LED client that communicates with daemon via socket"""
    
    def __init__(self):
        self.socket_path = '/tmp/motorpass_led.sock'
        self.daemon_available = self._check_daemon()
    
    def _check_daemon(self):
        """Check if LED daemon is running"""
        try:
            response = self._send_command({'action': 'ping'})
            return response and response.get('status') == 'ok'
        except:
            return False
    
    def _send_command(self, command, timeout=2.0):
        """Send command to LED daemon"""
        try:
            # Create socket connection
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            
            # Connect to daemon
            sock.connect(self.socket_path)
            
            # Send command
            sock.send(json.dumps(command).encode())
            
            # Receive response
            data = sock.recv(1024)
            response = json.loads(data.decode()) if data else {'status': 'no_response'}
            
            # Close connection
            sock.close()
            return response
            
        except socket.error:
            # Connection failed - daemon might be down
            self.daemon_available = False
            return {'status': 'connection_failed'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def is_available(self):
        """Check if LED system is available"""
        if not self.daemon_available:
            # Try to reconnect
            self.daemon_available = self._check_daemon()
        return self.daemon_available
    
    def set_state(self, state: LEDState, duration=None):
        """Set LED state"""
        command = {
            'action': 'set_state',
            'state': state.value,
        }
        if duration:
            command['duration'] = duration
        
        response = self._send_command(command)
        return response.get('status') == 'ok'
    
    def show_progress(self, percentage, color=(0, 255, 0)):
        """Show progress as filled ring (0-100%)"""
        command = {
            'action': 'progress',
            'percentage': max(0, min(100, percentage)),
            'color': list(color)
        }
        
        response = self._send_command(command)
        return response.get('status') == 'ok'
    
    def quick_flash(self, color=(255, 0, 0), times=3, speed=0.2):
        """Quick flash effect"""
        command = {
            'action': 'flash',
            'color': list(color),
            'times': times,
            'speed': speed
        }
        
        response = self._send_command(command)
        return response.get('status') == 'ok'
    
    def turn_off(self):
        """Turn off all LEDs"""
        response = self._send_command({'action': 'off'})
        return response.get('status') == 'ok'

# Global LED client instance
_led_client = None

def init_led_system(red_pin=18, green_pin=16):
    """
    Initialize LED client system
    red_pin and green_pin kept for compatibility but not used with daemon
    """
    global _led_client
    
    if _led_client is None:
        _led_client = LEDClient()
    
    available = _led_client.is_available()
    
    if available:
        print("✅ LED system connected to daemon")
    else:
        print("⚠️ LED daemon not available - LEDs disabled")
        print("💡 Start daemon with: sudo /home/capstone/MotorPass/myvenv/bin/python3 led_daemon.py")
    
    return available

# Your existing function names - COMPLETELY UNCHANGED!
def set_led_idle():
    """Set LED to idle/ready state (blue breathing)"""
    if _led_client and _led_client.is_available():
        return _led_client.set_state(LEDState.IDLE)
    return False

def set_led_processing():
    """Set LED to processing state (yellow rotating)"""
    if _led_client and _led_client.is_available():
        return _led_client.set_state(LEDState.PROCESSING)
    return False

def set_led_success(duration=3.0):
    """Set LED to success state (green solid) with auto-return to idle"""
    if _led_client and _led_client.is_available():
        return _led_client.set_state(LEDState.SUCCESS, duration)
    return False

def set_led_failed(duration=3.0):
    """Set LED to failed state (red solid) with auto-return to idle"""  
    if _led_client and _led_client.is_available():
        return _led_client.set_state(LEDState.FAILED, duration)
    return False

def set_led_camera():
    """Set LED to camera state (white breathing)"""
    if _led_client and _led_client.is_available():
        return _led_client.set_state(LEDState.CAMERA)
    return False

def set_led_off():
    """Turn off all LEDs"""
    if _led_client and _led_client.is_available():
        return _led_client.turn_off()
    return False

def cleanup_led_system():
    """Clean up LED client system"""
    global _led_client
    if _led_client:
        _led_client.turn_off()
        _led_client = None

def led_is_available():
    """Check if LED system is available"""
    return _led_client and _led_client.is_available()

def led_show_progress(percentage, color=(0, 255, 0)):
    """Show progress ring (0-100%)"""
    if _led_client and _led_client.is_available():
        return _led_client.show_progress(percentage, color)
    return False

def led_flash_success(times=3):
    """Flash green for success"""
    if _led_client and _led_client.is_available():
        return _led_client.quick_flash((0, 255, 0), times)
    return False

def led_flash_failed(times=3):
    """Flash red for failure"""
    if _led_client and _led_client.is_available():
        return _led_client.quick_flash((255, 0, 0), times)
    return False

def led_flash_warning(times=3):
    """Flash orange for warning"""
    if _led_client and _led_client.is_available():
        return _led_client.quick_flash((255, 165, 0), times)
    return False

# Context manager for automatic LED cleanup  
class LEDManager:
    def __init__(self, red_pin=18, green_pin=16):
        self.red_pin = red_pin
        self.green_pin = green_pin
    
    def __enter__(self):
        init_led_system(self.red_pin, self.green_pin)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        cleanup_led_system()

# Status reporting for debugging
def get_led_status():
    """Get LED system status for debugging"""
    if not _led_client:
        return {
            'available': False,
            'status': 'not_initialized',
            'daemon_running': False,
            'socket_path': '/tmp/motorpass_led.sock'
        }
    
    available = _led_client.is_available()
    return {
        'available': available,
        'status': 'connected' if available else 'daemon_unavailable',
        'daemon_running': available,
        'socket_path': _led_client.socket_path
    }

# Demo/test function
def demo():
    """Test LED client functionality"""
    print("🌟 MotorPass LED Client Test")
    print("=" * 40)
    
    # Initialize system
    available = init_led_system()
    
    if not available:
        print("❌ LED daemon not available")
        print("💡 Make sure daemon is running:")
        print("   sudo /home/capstone/MotorPass/myvenv/bin/python3 led_daemon.py")
        return False
    
    print("✅ LED client connected to daemon!")
    
    try:
        # Test all LED states
        test_states = [
            ('idle', 'Blue breathing (ready)', set_led_idle, 4),
            ('processing', 'Yellow rotating (scanning)', set_led_processing, 4),
            ('success', 'Green solid (success)', lambda: set_led_success(3), 4),
            ('failed', 'Red solid (failed)', lambda: set_led_failed(3), 4),
            ('camera', 'White breathing (camera)', set_led_camera, 4),
        ]
        
        for state, description, func, duration in test_states:
            print(f"\n🔄 Testing {state}: {description}")
            if func():
                print(f"   ✅ {state} command sent successfully")
            else:
                print(f"   ❌ {state} command failed")
            time.sleep(duration)
        
        # Test progress ring
        print(f"\n📊 Testing progress ring...")
        for i in range(0, 101, 25):
            print(f"   Progress: {i}%")
            if led_show_progress(i, (255, 165, 0)):  # Orange progress
                print(f"   ✅ Progress {i}% sent")
            time.sleep(1)
        
        # Test flash effects
        print(f"\n✨ Testing flash effects...")
        
        print("   Success flash (green)")
        if led_flash_success(3):
            print("   ✅ Success flash sent")
        time.sleep(2)
        
        print("   Failure flash (red)")
        if led_flash_failed(3):
            print("   ✅ Failure flash sent")
        time.sleep(2)
        
        print("   Warning flash (orange)")
        if led_flash_warning(3):
            print("   ✅ Warning flash sent")
        
        # Return to idle
        print(f"\n🏠 Returning to idle state...")
        set_led_idle()
        
        print(f"\n🎉 LED client test completed successfully!")
        return True
        
    except KeyboardInterrupt:
        print(f"\n🛑 Test interrupted by user")
        return False
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return False
    finally:
        cleanup_led_system()

if __name__ == "__main__":
    success = demo()
    exit(0 if success else 1)
