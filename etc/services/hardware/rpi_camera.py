# services/hardware/rpi_camera.py - Updated with Clean Camera Display

import cv2
import numpy as np
import time
import os
from datetime import datetime
from config import RPI_CAMERA_RESOLUTION, RPI_CAMERA_FRAMERATE, RPI_CAMERA_WARMUP_TIME

try:
    from picamera2 import Picamera2
    RPI_CAMERA_AVAILABLE = True
except ImportError:
    RPI_CAMERA_AVAILABLE = False

# Global camera instance and state tracking
_camera_instance = None
_camera_state = 'IDLE'  # IDLE, INITIALIZING, ACTIVE, CLEANING
_last_cleanup_time = 0
_cleanup_cooldown = 1.0  # Minimum seconds between cleanups

# Global variables for clean camera display
_cancel_clicked = False
_button_rect_global = None
_window_positions = {}  # Track window positions for centering


# ============== CLEAN CAMERA DISPLAY FUNCTIONS ==============

def create_clean_camera_window(window_name="Camera", width=640, height=480):
    """
    Create a clean camera window with no toolbar buttons
    
    Args:
        window_name: Name of the window
        width: Window width
        height: Window height
    """
    # Use WINDOW_NORMAL for better compatibility and responsiveness
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    
    # Set window size
    cv2.resizeWindow(window_name, width, height)
    
    # Set window to always be on top (hides taskbar)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)
    
    # Center the window
    try:
        import tkinter as tk
        root = tk.Tk()
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        root.destroy()
        
        x_pos = (screen_width - width) // 2
        y_pos = (screen_height - height) // 2
        cv2.moveWindow(window_name, x_pos, y_pos)
    except:
        pass  # If centering fails, just continue
    
    return width, height


def restore_taskbar():
    """
    Helper function to restore taskbar visibility
    Call this when you're done with the camera window
    """
    # Destroying all OpenCV windows will automatically restore taskbar
    cv2.destroyAllWindows()
    cv2.waitKey(1)


def add_cancel_button_overlay(frame, button_width=120, button_height=40, margin=20):
    """
    Add a clean cancel button overlay on the frame
    
    Args:
        frame: The camera frame to add button to
        button_width: Width of cancel button
        button_height: Height of cancel button
        margin: Margin from edges
    
    Returns:
        frame: Frame with button overlay
        button_rect: (x1, y1, x2, y2) coordinates of button for click detection
    """
    global _button_rect_global
    
    h, w = frame.shape[:2]
    
    # Position button at top-right
    x1 = w - button_width - margin
    y1 = margin
    x2 = x1 + button_width
    y2 = y1 + button_height
    
    # Draw semi-transparent background
    overlay = frame.copy()
    cv2.rectangle(overlay, (x1, y1), (x2, y2), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.5, frame, 0.5, 0, frame)
    
    # Draw red border
    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
    
    # Add "CANCEL" text
    text = "CANCEL"
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.6
    thickness = 2
    text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
    
    text_x = x1 + (button_width - text_size[0]) // 2
    text_y = y1 + (button_height + text_size[1]) // 2
    
    cv2.putText(frame, text, (text_x, text_y), font, font_scale, (255, 255, 255), thickness)
    
    _button_rect_global = (x1, y1, x2, y2)
    return frame, _button_rect_global


def check_cancel_click(x, y, button_rect):
    """
    Check if click coordinates are within cancel button
    
    Args:
        x, y: Click coordinates
        button_rect: (x1, y1, x2, y2) button rectangle
    
    Returns:
        bool: True if clicked inside button
    """
    if button_rect is None:
        return False
    x1, y1, x2, y2 = button_rect
    return x1 <= x <= x2 and y1 <= y <= y2


def camera_mouse_callback(event, x, y, flags, param):
    """Mouse callback to handle cancel button clicks"""
    global _cancel_clicked, _button_rect_global
    
    if event == cv2.EVENT_LBUTTONDOWN and _button_rect_global:
        if check_cancel_click(x, y, _button_rect_global):
            _cancel_clicked = True
            print("🛑 Cancel button clicked")


def reset_cancel_state():
    """Reset the cancel button state"""
    global _cancel_clicked
    _cancel_clicked = False


def is_cancel_clicked():
    """Check if cancel button was clicked"""
    return _cancel_clicked


# ============== CAMERA MANAGEMENT FUNCTIONS ==============

def force_camera_cleanup():
    """Smart cleanup of camera resources - only cleans when necessary"""
    global _camera_instance, _camera_state, _last_cleanup_time
    
    # Check if cleanup is needed
    current_time = time.time()
    if _camera_state == 'IDLE':
        print("✅ Camera already clean (IDLE state)")
        return
    
    if _camera_state == 'CLEANING':
        print("⏳ Camera cleanup already in progress...")
        return
        
    # Check cooldown period
    if current_time - _last_cleanup_time < _cleanup_cooldown:
        wait_time = _cleanup_cooldown - (current_time - _last_cleanup_time)
        print(f"⏳ Waiting {wait_time:.1f}s before cleanup (cooldown period)")
        time.sleep(wait_time)
    
    # Proceed with cleanup
    _camera_state = 'CLEANING'
    print("🧹 Smart camera cleanup...")
    
    # Destroy any OpenCV windows
    try:
        cv2.destroyAllWindows()
        cv2.waitKey(1)
    except:
        pass
    
    # Release camera instance if it exists
    if _camera_instance is not None:
        try:
            if hasattr(_camera_instance, 'camera') and _camera_instance.camera:
                try:
                    _camera_instance.camera.stop()
                except:
                    pass
                try:
                    _camera_instance.camera.close()
                except:
                    pass
            _camera_instance = None
        except:
            pass
    
    # Brief pause for resources to be freed
    time.sleep(0.5)
    
    # Update state
    _camera_state = 'IDLE'
    _last_cleanup_time = time.time()
    print("✅ Camera cleanup completed")


def get_camera():
    """Get camera instance with state tracking"""
    global _camera_instance, _camera_state
    
    # If camera is already active, return it
    if _camera_instance is not None and _camera_state == 'ACTIVE':
        return _camera_instance
    
    # If we're in a bad state, clean up first
    if _camera_state not in ['IDLE', 'ACTIVE']:
        force_camera_cleanup()
    
    # Initialize new camera instance
    if _camera_instance is None:
        _camera_state = 'INITIALIZING'
        _camera_instance = RPiCameraService()
        if _camera_instance.initialized:
            _camera_state = 'ACTIVE'
        else:
            _camera_state = 'IDLE'
            _camera_instance = None
    
    return _camera_instance


def release_camera():
    """Release camera instance"""
    force_camera_cleanup()


# ============== RPi CAMERA SERVICE CLASS ==============

class RPiCameraService:
    def __init__(self):
        self.camera = None
        self.initialized = False
        if RPI_CAMERA_AVAILABLE:
            self._initialize_camera()
    
    def _initialize_camera(self):
        """Initialize RPi Camera"""
        if not RPI_CAMERA_AVAILABLE:
            print("❌ RPi Camera not available")
            return False
            
        try:
            # Suppress libcamera logs
            os.environ['LIBCAMERA_LOG_LEVELS'] = 'ERROR'
            
            print("📷 Initializing camera...")
            self.camera = Picamera2()
            
            # Simple configuration
            config = self.camera.create_preview_configuration(
                main={"size": RPI_CAMERA_RESOLUTION}
            )
            
            self.camera.configure(config)
            self.camera.start()
            time.sleep(RPI_CAMERA_WARMUP_TIME)
            
            # Try to set autofocus silently
            try:
                from libcamera import controls
                self.camera.set_controls({
                    "AfMode": controls.AfModeEnum.Continuous,
                    "AfSpeed": controls.AfSpeedEnum.Fast,
                })
            except:
                pass
            
            self.initialized = True
            print("✅ Camera initialized successfully")
            return True
            
        except Exception as e:
            print(f"❌ Camera initialization failed: {e}")
            self.initialized = False
            return False
    
    def get_frame(self):
        """Get current frame from camera"""
        if not self.initialized or not self.camera:
            return None
        
        try:
            frame = self.camera.capture_array()
            
            # Convert format if needed
            if len(frame.shape) == 3:
                if frame.shape[2] == 4:  # RGBA format
                    frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2BGR)
                elif frame.shape[2] == 3:  # RGB format
                    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            
            return frame
        except Exception as e:
            print(f"⚠️ Error getting frame: {e}")
            return None
    
    def release(self):
        """Release camera resources"""
        if self.camera:
            try:
                self.camera.stop()
                self.camera.close()
            except:
                pass
        self.initialized = False


# ============== CONTEXT MANAGER ==============

class CameraContext:
    """Context manager that guarantees smart camera cleanup"""
    def __enter__(self):
        # No need to clean before if camera is idle
        if _camera_state != 'IDLE':
            force_camera_cleanup()
        self.camera = get_camera()
        return self.camera
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        force_camera_cleanup()
        return False


# ============== HELPER FUNCTIONS ==============

def ensure_camera_cleanup():
    """Wrapper for smart cleanup"""
    force_camera_cleanup()
