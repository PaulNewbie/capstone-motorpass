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



# ==========================
# GUEST-SPECIFIC MESSAGES
# ==========================

# Guest Registration
MSG_GUEST_NEW_REGISTRATION = "New guest - Opening registration form..."
MSG_GUEST_CANCELLED = "Guest registration cancelled"
MSG_GUEST_INFO_REQUIRED = "Please provide guest information..."

# Guest Status
MSG_GUEST_ALREADY_IN = "Guest already IN - Processing automatic TIMEOUT"
MSG_GUEST_TIMEOUT_SECURITY = "Security verification required for timeout..."
MSG_GUEST_TIMEOUT_SUCCESS = "Guest timeout successful"
MSG_GUEST_TIMEOUT_FAILED = "Failed to record guest timeout"

# Guest Detection
MSG_GUEST_STUDENT_STAFF_DETECTED = "Student/Staff NOT allowed as visitors"
MSG_GUEST_NAME_DETECTED = "Detected guest name: {name}"

# Guest Time Recording
MSG_GUEST_TIME_IN_PROCESSING = "Processing guest time in..."
MSG_GUEST_TIME_IN_SUCCESS = "Guest TIME IN recorded successfully"
MSG_GUEST_TIME_IN_FAILED = "Failed to record guest TIME IN"
MSG_GUEST_TIME_OUT_PROCESSING = "Recording guest TIME OUT..."
MSG_GUEST_TIME_OUT_SUCCESS = "Guest TIME OUT recorded successfully"
MSG_GUEST_TIME_OUT_FAILED = "Failed to record guest TIME OUT"

# Guest Verification
MSG_GUEST_VERIFICATION_SUCCESS = "Guest verification successful"
MSG_GUEST_VERIFICATION_FAILED = "Guest verification failed"
MSG_GUEST_LICENSE_RETAKE = "Retaking license scan..."

# Firebase Sync (Guest)
MSG_GUEST_FIREBASE_SYNCED = "Guest synced to Firebase"
MSG_GUEST_FIREBASE_FAILED = "Firebase sync failed"
