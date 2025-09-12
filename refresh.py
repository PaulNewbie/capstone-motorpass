# refresh.py - Simple F5 Soft Refresh System
"""
Simple F5 Refresh System for MotorPass
Press F5 to refresh stuck forms without killing the entire system
"""

import tkinter as tk
import threading
import time
import os
import glob

class SimpleRefreshManager:
    """Simple refresh manager - just does the essential cleanup"""
    
    def __init__(self):
        self.is_refreshing = False
        
    def setup_window(self, window):
        """Setup F5 refresh for any window"""
        window.bind('<F5>', lambda e: self.refresh())
        window.bind('<Control-r>', lambda e: self.refresh())
        
    def refresh(self):
        """Main refresh function"""
        if self.is_refreshing:
            return
            
        print(f"\n🔄 F5 REFRESH - {time.strftime('%H:%M:%S')}")
        
        # Run refresh in background to avoid blocking GUI
        threading.Thread(target=self._do_refresh, daemon=True).start()
        
    def _do_refresh(self):
        """Perform the actual refresh"""
        self.is_refreshing = True
        
        try:
            # 1. Hardware cleanup
            self._cleanup_hardware()
            
            # 2. Clear temp files
            self._clear_temp_files()
            
            # 3. Reset GUI forms
            self._reset_forms()
            
            print("✅ Refresh complete")
            
        except Exception as e:
            print(f"⚠️ Refresh error: {e}")
        finally:
            self.is_refreshing = False
            
    def _cleanup_hardware(self):
        """Clean up camera, LED, buzzer"""
        try:
            # LED cleanup
            from etc.services.hardware.led_control import set_led_idle, cleanup_led_system
            set_led_idle()
            
            # Buzzer cleanup  
            from etc.services.hardware.buzzer_control import cleanup_buzzer
            cleanup_buzzer()
            
            # Camera cleanup
            from etc.services.hardware.rpi_camera import force_camera_cleanup
            force_camera_cleanup()
            
            print("  ✅ Hardware cleaned")
            
        except Exception as e:
            print(f"  ⚠️ Hardware cleanup: {e}")
            
    def _clear_temp_files(self):
        try:
            patterns = [
                "temp_*.jpg", "temp_*.png", "license_*.jpg", 
                "captured_*.jpg", "helmet_*.jpg", "*.tmp"
            ]
            count = 0
            
            for pattern in patterns:
                for file in glob.glob(pattern):
                    try:
                        os.remove(file)
                        count += 1
                    except:
                        pass
                        
            if count > 0:
                print(f"  ✅ Cleared {count} temp files")
                
        except Exception as e:
            print(f"  ⚠️ File cleanup: {e}")
            
    def _reset_forms(self):
        """Enhanced form reset - better widget detection"""
        try:
            reset_count = 0
            
            for widget in self._get_all_widgets():
                try:
                    # Clear text inputs
                    if isinstance(widget, tk.Entry):
                        widget.delete(0, tk.END)
                        reset_count += 1
                        
                    # Clear text areas
                    elif isinstance(widget, tk.Text):
                        widget.delete(1.0, tk.END)
                        reset_count += 1
                        
                    # Reset string variables  
                    elif hasattr(widget, 'set') and hasattr(widget, 'get'):
                        try:
                            widget.set("")
                            reset_count += 1
                        except:
                            pass
                        
                    # Reset office selection buttons (improved detection)
                    elif isinstance(widget, tk.Button):
                        try:
                            current_bg = widget.cget('bg')
                            # Reset selected office buttons
                            if current_bg in ["#4CAF50", "#27AE60"]:  # Selected colors
                                widget.config(bg="#f0f0f0", fg="black")
                                reset_count += 1
                        except:
                            pass
                            
                except:
                    pass
                    
            print(f"  ✅ Reset {reset_count} form elements")
            
        except Exception as e:
            print(f"  ⚠️ Form reset: {e}")
            
    def _get_all_widgets(self):
        """Get all widgets from all windows"""
        widgets = []
        try:
            # Get all toplevel windows
            for window in tk._default_root.winfo_children():
                if isinstance(window, (tk.Toplevel, tk.Tk)):
                    widgets.extend(self._get_widgets_recursive(window))
        except:
            pass
        return widgets
        
    def _get_widgets_recursive(self, widget):
        """Recursively get all widgets"""
        widgets = [widget]
        try:
            for child in widget.winfo_children():
                widgets.extend(self._get_widgets_recursive(child))
        except:
            pass
        return widgets

# Global refresh manager
refresh_manager = SimpleRefreshManager()

def add_refresh_to_window(window):
    """
    Simple function to add F5 refresh to any window
    
    Usage:
        from simple_refresh import add_refresh_to_window
        add_refresh_to_window(self.root)
    """
    refresh_manager.setup_window(window)

def manual_refresh():
    """
    Function to trigger refresh manually (for refresh buttons)
    
    Usage:
        from simple_refresh import manual_refresh
        tk.Button(frame, text="Refresh", command=manual_refresh)
    """
    refresh_manager.refresh()

# Auto-setup for existing windows
def auto_setup_refresh():
    """Automatically setup refresh for existing windows"""
    try:
        root = tk._default_root
        if root:
            add_refresh_to_window(root)
            
            # Setup for any existing toplevel windows
            for child in root.winfo_children():
                if isinstance(child, tk.Toplevel):
                    add_refresh_to_window(child)
                    
    except:
        pass

"""
Press F5 or click the button to refresh.

WHAT IT DOES:
- Clears all form inputs and selections
- Resets LED to idle, stops buzzer, releases camera
- Removes temporary files
- Resets button states (like office selections)
- Shows progress in terminal
- No popups or dialogs
"""
