#!/usr/bin/env python3
"""
MotorPass LED Daemon - Background Service for WS281X LEDs
Run with: sudo ~/myvenv/bin/python3 led_daemon.py
"""

import socket
import os
import json
import threading
import time
import signal
import sys

class MotorPassLEDDaemon:
    def __init__(self):
        self.running = True
        self.sock = None
        self.strip = None
        self.Color = None
        self.current_animation_thread = None
        self.stop_animation = threading.Event()
        self.socket_path = '/tmp/motorpass_led.sock'
        
        # Initialize WS281X
        self._initialize_ws281x()
        # Setup socket
        self._setup_socket()
        # Setup signals
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _initialize_ws281x(self):
        """Initialize WS281X LEDs"""
        try:
            from rpi_ws281x import PixelStrip, Color
            
            LED_COUNT = 12
            LED_PIN = 18
            LED_FREQ_HZ = 800000
            LED_DMA = 10
            LED_BRIGHTNESS = 76
            LED_INVERT = False
            LED_CHANNEL = 0
            
            self.strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, 
                                  LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
            self.strip.begin()
            self.Color = Color
            
            print("✅ LED Daemon: WS281X initialized")
            self._test_flash()
            
        except ImportError:
            print("❌ rpi_ws281x not available")
            sys.exit(1)
        except Exception as e:
            print(f"❌ WS281X init failed: {e}")
            sys.exit(1)
    
    def _test_flash(self):
        """Quick blue flash"""
        try:
            for i in range(self.strip.numPixels()):
                self.strip.setPixelColor(i, self.Color(0, 0, 255))
            self.strip.show()
            time.sleep(0.2)
            self._clear_all()
        except:
            pass
    
    def _setup_socket(self):
        """Setup socket"""
        try:
            if os.path.exists(self.socket_path):
                os.unlink(self.socket_path)
            
            self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.sock.bind(self.socket_path)
            os.chmod(self.socket_path, 0o666)
            
            print(f"✅ Socket ready: {self.socket_path}")
            
        except Exception as e:
            print(f"❌ Socket setup failed: {e}")
            sys.exit(1)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown"""
        print(f"\n🛑 Shutting down...")
        self.shutdown()
    
    def _clear_all(self):
        """Turn off all LEDs"""
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, self.Color(0, 0, 0))
        self.strip.show()
    
    def _set_all_color(self, r, g, b):
        """Set all LEDs to color"""
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, self.Color(r, g, b))
        self.strip.show()
    
    def _stop_animation(self):
        """Stop current animation"""
        self.stop_animation.set()
        if self.current_animation_thread and self.current_animation_thread.is_alive():
            self.current_animation_thread.join(timeout=1.0)
        self.stop_animation.clear()
    
    def _breathing_animation(self, r, g, b, duration=3):
        """Breathing effect"""
        steps = 30
        step_delay = duration / (steps * 2)
        
        while not self.stop_animation.is_set() and self.running:
            # Fade in
            for i in range(steps):
                if self.stop_animation.is_set() or not self.running:
                    return
                brightness = i / (steps - 1)
                self._set_all_color(int(r * brightness), int(g * brightness), int(b * brightness))
                time.sleep(step_delay)
            
            # Fade out
            for i in range(steps - 1, -1, -1):
                if self.stop_animation.is_set() or not self.running:
                    return
                brightness = i / (steps - 1)
                self._set_all_color(int(r * brightness), int(g * brightness), int(b * brightness))
                time.sleep(step_delay)
    
    def _rotating_animation(self, r, g, b, speed=0.08):
        """Rotating effect"""
        tail_length = 3
        
        while not self.stop_animation.is_set() and self.running:
            for pos in range(self.strip.numPixels()):
                if self.stop_animation.is_set() or not self.running:
                    return
                
                self._clear_all()
                for i in range(tail_length):
                    pixel_pos = (pos - i) % self.strip.numPixels()
                    brightness = (tail_length - i) / tail_length
                    self.strip.setPixelColor(pixel_pos, self.Color(int(r * brightness), int(g * brightness), int(b * brightness)))
                
                self.strip.show()
                time.sleep(speed)
    
    def handle_command(self, command):
        """Handle LED command"""
        try:
            action = command.get('action')
            
            if action == 'set_state':
                state = command.get('state')
                duration = command.get('duration')
                self._handle_state_command(state, duration)
                
            elif action == 'progress':
                percentage = command.get('percentage', 0)
                color = command.get('color', [0, 255, 0])
                self._stop_animation()
                self._progress_ring(percentage, *color)
                
            elif action == 'flash':
                color = command.get('color', [255, 0, 0])
                times = command.get('times', 3)
                speed = command.get('speed', 0.2)
                self._stop_animation()
                self._quick_flash(*color, times, speed)
                
            elif action == 'off':
                self._stop_animation()
                self._clear_all()
                
            elif action == 'ping':
                return {'status': 'ok'}
                
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
        
        return {'status': 'ok'}
    
    def _handle_state_command(self, state, duration):
        """Handle state commands"""
        self._stop_animation()
        
        if state == 'idle':
            # Blue breathing
            self.current_animation_thread = threading.Thread(target=self._breathing_animation, args=(0, 0, 255, 3), daemon=True)
            self.current_animation_thread.start()
            
        elif state == 'processing':
            # Yellow rotating
            self.current_animation_thread = threading.Thread(target=self._rotating_animation, args=(255, 255, 0, 0.08), daemon=True)
            self.current_animation_thread.start()
            
        elif state == 'success':
            # Green solid
            self._set_all_color(0, 255, 0)
            if duration:
                def auto_return():
                    time.sleep(duration)
                    if self.running:
                        self._handle_state_command('idle', None)
                threading.Thread(target=auto_return, daemon=True).start()
                
        elif state == 'failed':
            # Red solid
            self._set_all_color(255, 0, 0)
            if duration:
                def auto_return():
                    time.sleep(duration)
                    if self.running:
                        self._handle_state_command('idle', None)
                threading.Thread(target=auto_return, daemon=True).start()
                
        elif state == 'camera':
            # White breathing
            self.current_animation_thread = threading.Thread(target=self._breathing_animation, args=(255, 255, 255, 1), daemon=True)
            self.current_animation_thread.start()
            
        elif state == 'off':
            self._clear_all()
    
    def _progress_ring(self, percentage, r, g, b):
        """Progress ring"""
        self._clear_all()
        leds_to_light = int(self.strip.numPixels() * percentage / 100)
        for i in range(leds_to_light):
            self.strip.setPixelColor(i, self.Color(r, g, b))
        self.strip.show()
    
    def _quick_flash(self, r, g, b, times, speed):
        """Quick flash"""
        for _ in range(times):
            if self.stop_animation.is_set() or not self.running:
                return
            self._set_all_color(r, g, b)
            time.sleep(speed)
            self._clear_all()
            time.sleep(speed)
    
    def run(self):
        """Main loop"""
        try:
            self.sock.listen(5)
            print("🌟 LED Daemon: Ready and listening...")
            
            while self.running:
                try:
                    self.sock.settimeout(1.0)
                    conn, addr = self.sock.accept()
                    self._handle_client(conn)
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:
                        print(f"⚠️ Connection error: {e}")
                    
        except Exception as e:
            print(f"❌ Main loop error: {e}")
        finally:
            self.shutdown()
    
    def _handle_client(self, conn):
        """Handle client connection"""
        try:
            data = conn.recv(1024)
            if not data:
                return
            
            command = json.loads(data.decode())
            response = self.handle_command(command)
            
            if response:
                conn.send(json.dumps(response).encode())
                
        except Exception as e:
            print(f"⚠️ Client error: {e}")
        finally:
            try:
                conn.close()
            except:
                pass
    
    def shutdown(self):
        """Clean shutdown"""
        print("🛑 Shutting down...")
        self.running = False
        self._stop_animation()
        
        if self.strip:
            self._clear_all()
        
        if self.sock:
            try:
                self.sock.close()
            except:
                pass
        
        if os.path.exists(self.socket_path):
            try:
                os.unlink(self.socket_path)
            except:
                pass
        
        print("✅ Shutdown complete")

def main():
    if os.geteuid() != 0:
        print("❌ Must run as root: sudo ~/myvenv/bin/python3 led_daemon.py")
        sys.exit(1)
    
    daemon = MotorPassLEDDaemon()
    try:
        daemon.run()
    except KeyboardInterrupt:
        pass
    finally:
        daemon.shutdown()

if __name__ == "__main__":
    main()
