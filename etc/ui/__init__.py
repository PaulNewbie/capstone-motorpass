# ui/__init__.py - Clean UI Module Initialization
"""
MotorPass UI Module
This module contains all GUI interfaces for the MotorPass system:
- main_window.py: Main menu interface
- views/student_view.py: Student/Staff verification GUI (refactored)
- guest_gui.py: Guest verification GUI
- views/admin_views.py: Admin panel GUI (refactored)
- student_gui.py: BACKUP ONLY - not imported
"""

# Import working components
print("Loading UI components...")

try:
    from .main_window import MotorPassGUI
    print("✅ MotorPassGUI loaded")
except ImportError as e:
    print(f"❌ Could not import MotorPassGUI: {e}")
    MotorPassGUI = None

try:
    from .views.student_view import StudentVerificationView as StudentVerificationGUI
    print("✅ StudentVerificationGUI loaded (refactored)")
except ImportError as e:
    print(f"❌ Could not import StudentVerificationGUI: {e}")
    StudentVerificationGUI = None

try:
    from .guest_gui import GuestVerificationGUI
    print("✅ GuestVerificationGUI loaded")
except ImportError as e:
    print(f"❌ Could not import GuestVerificationGUI: {e}")
    GuestVerificationGUI = None

try:
    from .views.admin_views import AdminPanelGUI
    print("✅ AdminPanelGUI loaded")
except ImportError as e:
    print(f"❌ Could not import AdminPanelGUI: {e}")
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

print(f"✅ UI Module loaded - Available components: {__all__}")

# Module version
__version__ = '1.0.0'
