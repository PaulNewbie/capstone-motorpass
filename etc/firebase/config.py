# firebase/config.py - Simple Firebase Configuration

# =================== FIREBASE SETTINGS ===================

# **IMPORTANT: CHANGE THIS TO YOUR PROJECT ID!**
FIREBASE_PROJECT_ID = "motorpass-456a0" 

# Firebase credentials file 
FIREBASE_CREDENTIALS = "json_folder/firebase_credentials.json"

# =================== COLLECTION NAMES ===================

# These are the collections that will be created in Firebase
COLLECTIONS = {
    'guests': 'guests',
    'staff': 'staff',
    'students': 'students',
    'time_tracking': 'time_tracking',
    'current_status': 'current_status',
    'vip_records': 'vip_records'
}

# =================== SYNC SETTINGS ===================

# How often to check for internet connection (seconds)
CONNECTION_CHECK_INTERVAL = 30

# Maximum items to keep in offline queue  
MAX_QUEUE_SIZE = 1000

# File to store offline sync queue
SYNC_QUEUE_FILE = "json_folder/firebase_sync_queue.json"
