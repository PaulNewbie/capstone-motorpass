# ui/__init__.py - UI Module with Optional Verbose Loading
"""
MotorPass UI Module
This module contains all GUI interfaces for the MotorPass system.
Set UI_VERBOSE=1 environment variable for detailed loading info.
"""

import os

# Check if verbose mode is enabled
VERBOSE = os.environ.get('UI_VERBOSE', '0') == '1'

def log(message):
    """Log message if verbose mode is enabled"""
    if VERBOSE:
        print(message)

# Import working components
if VERBOSE:
    log("Loading UI components...")

try:
    from .main_window import MotorPassGUI
    log("✅ MotorPassGUI loaded")
except ImportError as e:
    if VERBOSE:
        log(f"❌ Could not import MotorPassGUI: {e}")
    MotorPassGUI = None

try:
    from .views.student_view import StudentVerificationView as StudentVerificationGUI
    log("✅ StudentVerificationGUI loaded (refactored)")
except ImportError as e:
    if VERBOSE:
        log(f"❌ Could not import StudentVerificationGUI: {e}")
    StudentVerificationGUI = None

try:
    from .guest_gui import GuestVerificationGUI
    log("✅ GuestVerificationGUI loaded")
except ImportError as e:
    if VERBOSE:
        log(f"❌ Could not import GuestVerificationGUI: {e}")
    GuestVerificationGUI = None

try:
    from .views.admin_views import AdminPanelGUI
    log("✅ AdminPanelGUI loaded")
except ImportError as e:
    if VERBOSE:
        log(f"❌ Could not import AdminPanelGUI: {e}")
    AdminPanelGUI = None

# Export successfully imported components
__all__ = []
if MotorPassGUI:
    __all__.append('MotorPassGUI')
if StudentVerificationGUI:
    __all__.append('StudentVerificationGUI')
if GuestVerificationGUI:
    __all__.append('GuestVerificationGUI')
if AdminPanelGUI:
    __all__.append('AdminPanelGUI')

if VERBOSE:
    log(f"✅ UI Module loaded - Available components: {__all__}")

# Module version
__version__ = '1.0.0'
