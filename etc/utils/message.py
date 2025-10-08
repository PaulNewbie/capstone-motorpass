# etc/utils/messages.py
"""
Centralized message constants for verification system
Makes it easy to update messages in one place
"""

# ============= SUCCESS MESSAGES =============
MSG_TIME_IN_RECORDED = "✅ TIME IN recorded at {timestamp}"
MSG_TIME_OUT_RECORDED = "✅ TIME OUT recorded at {timestamp}"
MSG_MANUAL_OVERRIDE_SUCCESS = "✅ Manual override successful"
MSG_MANUAL_OVERRIDE_GRANTED = "✅ Manual override GRANTED - Attempt {attempt}"
MSG_VERIFICATION_SUCCESS = "✅ Verification successful"
MSG_HELMET_VERIFIED = "✅ Helmet verified successfully!"
MSG_LICENSE_VERIFIED = "✅ License verification successful"

# ============= ERROR MESSAGES =============
MSG_MANUAL_OVERRIDE_FAILED = "Manual override failed"
MSG_MANUAL_OVERRIDE_DENIED = "❌ Manual override DENIED - Name mismatch on attempt {attempt}"
MSG_MANUAL_OVERRIDE_DENIED_ALL = "❌ Manual override DENIED - Both attempts failed"
MSG_MANUAL_CANCELLED = "❌ Manual input attempt {attempt} cancelled"
MSG_STUDENT_PERMIT_DENIED = "Student Permit not allowed"
MSG_STUDENT_LICENSE_DENIED = "Student Driver License not allowed"
MSG_TIME_IN_FAILED = "Failed to record TIME IN"
MSG_TIME_OUT_FAILED = "Failed to record TIME OUT"
MSG_HELMET_FAILED = "Helmet verification failed"
MSG_FINGERPRINT_FAILED = "Fingerprint authentication failed after 2 attempts"
MSG_LICENSE_EXPIRED = "License has expired"
MSG_LICENSE_VERIFICATION_FAILED = "License verification failed"

# ============= STATUS MESSAGES =============
MSG_CLEANUP_IMAGE = "🗑️ Cleaned up image file"
MSG_FINAL_CLEANUP = "🗑️ Final cleanup of image file"
MSG_STARTING_VERIFICATION = "🚀 Starting verification process..."
MSG_CHECKING_HELMET = "🪖 Checking helmet... (Check terminal for camera)"
MSG_CHECKING_FINGERPRINT = "🔍 Please place your finger on the scanner"
MSG_CHECKING_LICENSE = "📄 Capturing license... (Check terminal for camera)"
MSG_PROCESSING_TIME_OUT = "🚪 Processing TIME OUT - No license scan needed"
MSG_AUTO_RETRY = "🔄 Auto-retrying license scan..."

# ============= WARNING MESSAGES =============
MSG_FIRST_ATTEMPT_FAILED = "⚠️ FIRST ATTEMPT FAILED - Auto-retrying..."
MSG_SECOND_ATTEMPT_FAILED = "⚠️ Second attempt verification failed"
MSG_LICENSE_EXPIRED_WARNING = "⚠️ License expired {days} days ago - Access denied"
MSG_MANUAL_INPUT_OPTION = "🤔 MANUAL INPUT OPTION:"

# ============= INFO MESSAGES =============
MSG_EXPECTED_NAME = "   Expected: {name}"
MSG_DETECTED_NAME = "   Detected: {name}"
MSG_PROCESSING_IMAGE = "   📁 Processing image: {filename}"
MSG_CURRENT_STATUS = "🔍 Current status for {name}: {status}"

# ============= CAMERA/DETECTION MESSAGES =============
MSG_CAMERA_TERMINAL = "(Check terminal for camera)"
MSG_HELMET_TERMINAL = "🪖 HELMET VERIFICATION (Terminal Camera)"
MSG_LICENSE_TERMINAL = "📄 LICENSE CAPTURE (Terminal Camera)"
MSG_LICENSE_ATTEMPT = "📷 License attempt {attempt}/2"

# ============= SEPARATORS =============
SEPARATOR_LONG = "=" * 60
SEPARATOR_SHORT = "=" * 30
