# ui/components/window_helpers.py - Window Management Components
# KISS principle: Simple window management functions used across all GUIs

import tkinter as tk
from datetime import datetime

class WindowManager:
    """Reusable window management components for consistent behavior across all GUIs"""
    
    @staticmethod
    def setup_fullscreen_window(root, title, bg_color='#FFFFFF'):
        """Setup a responsive fullscreen window with consistent behavior
        
        Args:
            root: tkinter root/Toplevel window
            title: Window title
            bg_color: Background color
            
        Returns:
            dict: Screen information for responsive calculations
        """
        root.title(title)
        root.configure(bg=bg_color)
        
        # Get screen dimensions
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        
        # Calculate display characteristics
        aspect_ratio = screen_width / screen_height
        is_square_display = abs(aspect_ratio - 1.0) < 0.3  # Within 30% of square (1024x768 = 1.33)
        is_wide_display = aspect_ratio > 1.5  # Wider than 3:2
        
        # Set base size for responsive calculations
        if is_square_display:
            display_size = min(screen_width, screen_height)
        else:
            display_size = min(screen_width, screen_height)
        
        # Set fullscreen geometry
        root.geometry(f"{screen_width}x{screen_height}")
        root.resizable(False, False)
        
        # Make window fullscreen and hide taskbar
        try:
            # Try Windows method first
            root.state('zoomed')
            # Hide taskbar by making window truly fullscreen
            root.attributes('-fullscreen', True)
        except:
            # Fallback for other platforms
            try:
                root.attributes('-zoomed', True)
                root.attributes('-fullscreen', True)
            except:
                # Final fallback - just maximize
                root.state('normal')
                root.geometry(f"{screen_width}x{screen_height}+0+0")
        
        # Return screen information for responsive calculations
        return {
            'screen_width': screen_width,
            'screen_height': screen_height,
            'aspect_ratio': aspect_ratio,
            'is_square_display': is_square_display,
            'is_wide_display': is_wide_display,
            'display_size': display_size
        }
    
    @staticmethod
    def setup_modal_window(parent, title, width, height, bg_color='#FFFFFF'):
        """Setup a centered modal window - FIXED for grab_set issue
        
        Args:
            parent: Parent window
            title: Window title
            width, height: Window dimensions
            bg_color: Background color
            
        Returns:
            tkinter.Toplevel: The created modal window
        """
        modal = tk.Toplevel(parent)
        modal.title(title)
        modal.configure(bg=bg_color)
        modal.resizable(False, False)
        
        # Center the window
        screen_width = modal.winfo_screenwidth()
        screen_height = modal.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        modal.geometry(f"{width}x{height}+{x}+{y}")
        
        # Make it transient first
        modal.transient(parent)
        
        # IMPORTANT: Update and wait for window to be ready
        modal.update_idletasks()
        modal.update()  # Force window to be drawn
        
        # Now safely set grab - with error handling
        try:
            modal.grab_set()
        except tk.TclError as e:
            print(f"Warning: Could not set modal grab - {e}")
            # Window will still work, just won't be fully modal
        
        return modal
    
    @staticmethod
    def bind_fullscreen_controls(root, on_toggle=None, on_close=None):
        """Bind standard fullscreen control keys
        
        Args:
            root: tkinter window
            on_toggle: Optional callback for fullscreen toggle
            on_close: Optional callback for window close
        """
        def toggle_fullscreen(event=None):
            """Toggle fullscreen mode"""
            try:
                current_state = root.attributes('-fullscreen')
                root.attributes('-fullscreen', not current_state)
                
                if current_state:
                    print("Exited fullscreen mode (Taskbar visible)")
                else:
                    print("Entered fullscreen mode (Taskbar hidden)")
                
                # Call custom callback if provided
                if on_toggle:
                    on_toggle(not current_state)
                    
            except Exception as e:
                print(f"Error toggling fullscreen: {e}")
        
        def handle_close(event=None):
            """Handle window close"""
            if on_close:
                on_close()
            else:
                try:
                    root.quit()
                    root.destroy()
                except:
                    pass
        
        # Bind standard keys
        root.bind('<F11>', toggle_fullscreen)
        root.bind('<Escape>', handle_close)
        
        return toggle_fullscreen
    
    @staticmethod
    def create_time_manager(root):
        """Create a time manager for live time displays
        
        Args:
            root: tkinter window
            
        Returns:
            dict: Time StringVars and update function
        """
        time_string = tk.StringVar()
        date_string = tk.StringVar()
        
        def update_time():
            """Update time display"""
            try:
                if not hasattr(root, 'winfo_exists') or not root.winfo_exists():
                    return
                    
                now = datetime.now()
                time_string.set(now.strftime("%I:%M:%S %p"))
                date_string.set(now.strftime("%A, %B %d, %Y"))
                
                if root.winfo_exists():
                    root.after(1000, update_time)
            except:
                pass
        
        # Start the clock
        update_time()
        
        return {
            'time_string': time_string,
            'date_string': date_string,
            'update_function': update_time
        }


class ResponsiveCalculator:
    """Helper class for responsive UI calculations"""
    
    @staticmethod
    def get_font_sizes(screen_info, gui_type='admin'):
        """Calculate responsive font sizes based on screen info
        
        Args:
            screen_info: Dict from setup_fullscreen_window()
            gui_type: Type of GUI ('admin', 'student', 'guest', 'main')
            
        Returns:
            dict: Font sizes for different UI elements
        """
        screen_width = screen_info['screen_width']
        screen_height = screen_info['screen_height']
        display_size = screen_info['display_size']
        is_square_display = screen_info['is_square_display']
        is_wide_display = screen_info['is_wide_display']
        
        if gui_type == 'admin':
            return {
                'title': max(16, int(display_size / 50)),
                'subtitle': max(10, int(display_size / 80)),
                'button': max(11, int(display_size / 75)),
                'card_title': max(11, int(display_size / 75)),
                'card_description': max(8, int(display_size / 100)),
                'card_icon': max(24, int(display_size / 35)),
                'stat_label': max(9, int(display_size / 90)),
                'stat_value': max(16, int(display_size / 50)),
                'time': max(12, int(display_size / 65)),
                'date': max(7, int(display_size / 120))
            }
        
        elif gui_type == 'main':
            if is_square_display:
                return {
                    'title': max(18, int(screen_width / 60)),
                    'subtitle': max(8, int(screen_width / 140)),
                    'button': max(12, int(screen_width / 90))
                }
            elif is_wide_display:
                return {
                    'title': max(20, int(screen_height / 35)),
                    'subtitle': max(10, int(screen_height / 110)),
                    'button': max(14, int(screen_height / 65))
                }
            else:
                return {
                    'title': max(19, int(display_size / 45)),
                    'subtitle': max(9, int(display_size / 120)),
                    'button': max(13, int(display_size / 80))
                }
        
        elif gui_type in ['student', 'guest']:
            return {
                'title': max(16, int(display_size / 50)),
                'subtitle': max(12, int(display_size / 70)),
                'status': max(10, int(display_size / 80)),
                'button': max(12, int(display_size / 70)),
                'time': max(14, int(display_size / 60)),
                'step': max(11, int(display_size / 75))
            }
        
        # Default fallback
        return {
            'title': 16, 'subtitle': 10, 'button': 12, 'time': 14
        }
    
    @staticmethod
    def get_padding_sizes(screen_info):
        """Calculate responsive padding sizes
        
        Args:
            screen_info: Dict from setup_fullscreen_window()
            
        Returns:
            dict: Padding sizes for different UI elements
        """
        screen_width = screen_info['screen_width']
        screen_height = screen_info['screen_height']
        
        return {
            'content_x': max(20, int(screen_width * 0.02)),
            'content_y': max(15, int(screen_height * 0.015)),
            'card_spacing': max(6, int(screen_width * 0.008)),
            'button_padding': max(8, int(screen_width * 0.01)),
            'section_spacing': max(15, int(screen_height * 0.02))
        }
    
    @staticmethod
    def get_window_sizes(screen_info, window_type='modal'):
        """Calculate responsive window sizes
        
        Args:
            screen_info: Dict from setup_fullscreen_window()
            window_type: Type of window ('modal', 'large_modal', 'sidebar')
            
        Returns:
            dict: Width and height for the window type
        """
        screen_width = screen_info['screen_width']
        screen_height = screen_info['screen_height']
        
        if window_type == 'modal':
            return {
                'width': max(400, int(screen_width * 0.4)),
                'height': max(300, int(screen_height * 0.4))
            }
        elif window_type == 'large_modal':
            return {
                'width': max(600, int(screen_width * 0.6)),
                'height': max(500, int(screen_height * 0.6))
            }
        elif window_type == 'sidebar':
            return {
                'width': max(200, int(screen_width * 0.20)),
                'height': screen_height
            }
        
        return {'width': 400, 'height': 300}


class WindowIntegration:
    """Integration helpers for adding refresh and other common features"""
    
    @staticmethod
    def setup_refresh_integration(root):
        """Setup F5 refresh integration if available
        
        Args:
            root: tkinter window
        """
        try:
            from refresh import add_refresh_to_window
            if add_refresh_to_window:
                add_refresh_to_window(root)
                return True
        except ImportError:
            pass
        return False
    
    @staticmethod
    def create_status_manager(root):
        """Create a status text manager for GUI status updates
        
        Args:
            root: tkinter window
            
        Returns:
            dict: Status StringVar and helper functions
        """
        status_text = tk.StringVar(value="Ready")
        
        def set_status(message, duration=None):
            """Set status message with optional auto-clear"""
            status_text.set(message)
            if duration:
                root.after(duration * 1000, lambda: status_text.set("Ready"))
        
        def clear_status():
            """Clear status message"""
            status_text.set("Ready")
        
        return {
            'status_var': status_text,
            'set_status': set_status,
            'clear_status': clear_status
        }
    
    @staticmethod
    def setup_common_gui_features(root, title, bg_color='#FFFFFF', enable_refresh=True):
        """Setup all common GUI features in one call
        
        Args:
            root: tkinter window
            title: Window title
            bg_color: Background color
            enable_refresh: Whether to enable F5 refresh
            
        Returns:
            dict: Complete GUI setup information
        """
        # Setup fullscreen window
        screen_info = WindowManager.setup_fullscreen_window(root, title, bg_color)
        
        # Setup fullscreen controls
        toggle_func = WindowManager.bind_fullscreen_controls(root)
        
        # Setup time manager
        time_manager = WindowManager.create_time_manager(root)
        
        # Setup status manager
        status_manager = WindowIntegration.create_status_manager(root)
        
        # Setup refresh integration
        refresh_enabled = False
        if enable_refresh:
            refresh_enabled = WindowIntegration.setup_refresh_integration(root)
        
        # Calculate responsive sizes
        font_sizes = ResponsiveCalculator.get_font_sizes(screen_info)
        padding_sizes = ResponsiveCalculator.get_padding_sizes(screen_info)
        
        return {
            'screen_info': screen_info,
            'time_manager': time_manager,
            'status_manager': status_manager,
            'font_sizes': font_sizes,
            'padding_sizes': padding_sizes,
            'toggle_fullscreen': toggle_func,
            'refresh_enabled': refresh_enabled
        }
