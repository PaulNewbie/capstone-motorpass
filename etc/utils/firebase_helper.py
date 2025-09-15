# firebase_helper.py 

import os
import sys

def safe_firebase_sync(sync_function, *args, **kwargs):
    """Safely call Firebase sync functions with error handling"""
    try:
        # Try to import Firebase functions
        from etc.firebase.sync import add_guest as firebase_add_guest, record_entry, get_status
        
        # Call the requested function
        if sync_function == 'add_guest':
            return firebase_add_guest(*args, **kwargs)
        elif sync_function == 'record_entry':
            return record_entry(*args, **kwargs)
        elif sync_function == 'get_status':
            return get_status(*args, **kwargs)
        else:
            print(f"??  Unknown sync function: {sync_function}")
            return None
            
    except ImportError as e:
        print(f"??  Firebase not available: {e}")
        print("?? Install with: pip install firebase-admin")
        return None
    except Exception as e:
        print(f"??  Firebase sync error: {e}")
        print("?? Check firebase_credentials.json and config")
        return None

def sync_guest_to_firebase(name, plate_number, office):
    """Add guest to Firebase safely"""
    return safe_firebase_sync('add_guest', name, plate_number, office)

def sync_time_to_firebase(user_id, name, user_type, action):
    """Record time entry to Firebase safely"""
    return safe_firebase_sync('record_entry', user_id, name, user_type, action)

def check_firebase_status():
    """Check Firebase status safely"""
    return safe_firebase_sync('get_status')
