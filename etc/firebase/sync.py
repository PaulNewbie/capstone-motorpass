# firebase/sync.py - Main Firebase Sync Functions

import sqlite3
import os
import sys
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Import our modules
from etc.firebase.config import FIREBASE_PROJECT_ID, FIREBASE_CREDENTIALS, COLLECTIONS
from etc.firebase.queue import queue_manager
from database.init_database import MOTORPASS_DB

# Try to import Firebase
try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    firebase_available = True
except ImportError:
    print("Install with: pip install firebase-admin")
    firebase_available = False

# =================== FIREBASE CONNECTION ===================

firebase_db = None
firebase_ready = False

_last_connection_check = 0
_last_connection_result = False
_connection_cache_duration = 10 

def init_firebase():
    """Initialize Firebase connection (call this once)"""
    global firebase_db, firebase_ready
    
    if firebase_ready:
        return True
    
    try:
        if not firebase_available:
            print("❌ Firebase SDK not available")
            return False
            
        if not os.path.exists(FIREBASE_CREDENTIALS):
            print(f"❌ Firebase credentials not found: {FIREBASE_CREDENTIALS}")
            print("💡 Download from Firebase Console and save as firebase_credentials.json")
            return False
        
        # Clear existing Firebase apps
        if firebase_admin._apps:
            firebase_admin._apps.clear()
        
        # Initialize Firebase
        cred = credentials.Certificate(FIREBASE_CREDENTIALS)
        firebase_admin.initialize_app(cred, {'projectId': FIREBASE_PROJECT_ID})
        
        firebase_db = firestore.client()
        firebase_ready = True
        
        print("✅ Firebase connected successfully")
        return True
        
    except Exception as e:
        print(f"❌ Firebase connection failed: {e}")
        firebase_ready = False
        return False

def is_online():
    """Check internet connection with caching."""
    global _last_connection_check, _last_connection_result, _connection_cache_duration
    
    import time
    current_time = time.time()
    
    # Use cached result if recent to avoid repeated checks
    if current_time - _last_connection_check < _connection_cache_duration:
        return _last_connection_result
    
    try:
        import socket
        
        # Try to connect to Google's DNS with a short timeout
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)  # Set a 2-second timeout for the connection attempt
        result = sock.connect_ex(("8.8.8.8", 53))
        sock.close()
        
        is_connected = (result == 0)
        
        # Cache the result
        _last_connection_result = is_connected
        _last_connection_check = current_time
        
        if is_connected:
            print("🌐 Connection check: ONLINE")
        else:
            print("📴 Connection check: OFFLINE")
            
        return is_connected
        
    except socket.error:
        _last_connection_result = False
        _last_connection_check = current_time
        print("📴 Connection check: OFFLINE (socket error)")
        return False
        
# =================== CLEAN SYNC FUNCTIONS ===================

def add_guest(name, plate_number, office):
    """Add guest to database and sync to Firebase
    
    Args:
        name (str): Guest full name
        plate_number (str): Vehicle plate number  
        office (str): Office they're visiting
        
    Returns:
        int: Guest ID if successful, None if failed
    """
    try:
        current_time = datetime.now().isoformat()
        
        # 1. ALWAYS save to local database first
        conn = sqlite3.connect(MOTORPASS_DB)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO guests (full_name, plate_number, office_visiting, created_date)
            VALUES (?, ?, ?, ?)
        ''', (name, plate_number, office, current_time))
        
        guest_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # 2. Prepare data for Firebase
        guest_data = {
            'guest_id': guest_id,
            'full_name': name,
            'plate_number': plate_number,
            'office_visiting': office,
            'created_date': current_time
        }
        
        # 3. Try to sync to Firebase (online) or queue (offline)
        if is_online():
            try:
                firebase_db.collection(COLLECTIONS['guests']).document(str(guest_id)).set({
                    **guest_data,
                    'synced_at': firestore.SERVER_TIMESTAMP
                }, timeout=5)
                print(f"🔥 Guest synced instantly: {name}")
            except Exception as e:
                print(f"⚠️  Instant sync failed, queuing: {e}")
                queue_manager.add_to_queue('guests', str(guest_id), guest_data)
        else:
            print(f"📴 Offline - Guest queued for sync: {name}")
            queue_manager.add_to_queue('guests', str(guest_id), guest_data)
        
        print(f"✅ Guest added: {name}")
        return guest_id
        
    except Exception as e:
        print(f"❌ Error adding guest: {e}")
        return None

def record_entry(user_id, user_name, user_type, action):
    """Record time entry and sync to Firebase
    
    Args:
        user_id (str): User ID (student_id, staff_no, or plate_number)
        user_name (str): User full name
        user_type (str): 'STUDENT', 'STAFF', or 'GUEST'  
        action (str): 'IN' or 'OUT'
        
    Returns:
        bool: True if successful, False if failed
    """
    try:
        current_time = datetime.now()
        date_str = current_time.strftime('%Y-%m-%d')
        time_str = current_time.strftime('%H:%M:%S')
        timestamp_str = current_time.isoformat()
        
        # 1. ALWAYS save to local database first
        conn = sqlite3.connect(MOTORPASS_DB)
        cursor = conn.cursor()
        
        # Add to time_tracking table
        cursor.execute('''
            INSERT INTO time_tracking (user_id, user_name, user_type, action, date, time, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, user_name, user_type, action, date_str, time_str, timestamp_str))
        
        time_record_id = cursor.lastrowid
        
        # Update current_status table
        cursor.execute('''
            INSERT OR REPLACE INTO current_status (user_id, user_name, user_type, status, last_action_time)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, user_name, user_type, action, timestamp_str))
        
        conn.commit()
        conn.close()
        
        # 2. Prepare data for Firebase
        time_data = {
            'id': time_record_id,
            'user_id': user_id,
            'user_name': user_name,
            'user_type': user_type,
            'action': action,
            'date': date_str,
            'time': time_str,
            'timestamp': timestamp_str
        }
        
        status_data = {
            'user_id': user_id,
            'user_name': user_name,
            'user_type': user_type,
            'status': action,
            'last_action_time': timestamp_str
        }
        
        # 3. Try to sync to Firebase (online) or queue (offline)
        if is_online():
            try:
                # Sync time tracking
                firebase_db.collection(COLLECTIONS['time_tracking']).document(str(time_record_id)).set({
                    **time_data,
                    'synced_at': firestore.SERVER_TIMESTAMP
                },timeout=5)
                
                # Sync current status
                firebase_db.collection(COLLECTIONS['current_status']).document(str(user_id)).set({
                    **status_data,
                    'synced_at': firestore.SERVER_TIMESTAMP
                },timeout=5)
                
                print(f"🔥 Time entry synced instantly: {user_name} - {action}")
                
            except Exception as e:
                print(f"⚠️  Instant sync failed, queuing: {e}")
                queue_manager.add_to_queue('time_tracking', str(time_record_id), time_data)
                queue_manager.add_to_queue('current_status', str(user_id), status_data)
        else:
            print(f"📴 Offline - Time entry queued: {user_name} - {action}")
            queue_manager.add_to_queue('time_tracking', str(time_record_id), time_data)
            queue_manager.add_to_queue('current_status', str(user_id), status_data)
        
        print(f"✅ Time recorded: {user_name} - {action}")
        return True
        
    except Exception as e:
        print(f"❌ Error recording time: {e}")
        return False

def add_staff(staff_no, name, role, license_num=None, plate_num=None):
    """Add staff member and sync to Firebase
    
    Args:
        staff_no (str): Staff number/ID
        name (str): Staff full name
        role (str): Staff role/position
        license_num (str, optional): License number
        plate_num (str, optional): Plate number
        
    Returns:
        bool: True if successful, False if failed
    """
    try:
        current_time = datetime.now().isoformat()
        
        # 1. ALWAYS save to local database first
        conn = sqlite3.connect(MOTORPASS_DB)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO staff 
            (staff_no, full_name, staff_role, license_number, plate_number, enrolled_date, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (staff_no, name, role, license_num, plate_num, current_time, current_time))
        
        conn.commit()
        conn.close()
        
        # 2. Prepare data for Firebase
        staff_data = {
            'staff_no': staff_no,
            'full_name': name,
            'staff_role': role,
            'license_number': license_num,
            'plate_number': plate_num,
            'enrolled_date': current_time,
            'last_updated': current_time
        }
        
        # 3. Try to sync to Firebase (online) or queue (offline)
        if is_online():
            try:
                firebase_db.collection(COLLECTIONS['staff']).document(str(staff_no)).set({
                    **staff_data,
                    'synced_at': firestore.SERVER_TIMESTAMP
                }, timeout=5)
                print(f"🔥 Staff synced instantly: {name}")
            except Exception as e:
                print(f"⚠️  Instant sync failed, queuing: {e}")
                queue_manager.add_to_queue('staff', str(staff_no), staff_data)
        else:
            print(f"📴 Offline - Staff queued for sync: {name}")
            queue_manager.add_to_queue('staff', str(staff_no), staff_data)
        
        print(f"✅ Staff added: {name}")
        return True
        
    except Exception as e:
        print(f"❌ Error adding staff: {e}")
        return False

def add_student(student_id, name, course, license_num=None, plate_num=None):
    """Add student and sync to Firebase
    
    Args:
        student_id (str): Student ID number
        name (str): Student full name
        course (str): Student course/program
        license_num (str, optional): License number
        plate_num (str, optional): Plate number
        
    Returns:
        bool: True if successful, False if failed
    """
    try:
        current_time = datetime.now().isoformat()
        
        # 1. ALWAYS save to local database first
        conn = sqlite3.connect(MOTORPASS_DB)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO students 
            (student_id, full_name, course, license_number, plate_number, enrolled_date, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (student_id, name, course, license_num, plate_num, current_time, current_time))
        
        conn.commit()
        conn.close()
        
        # 2. Prepare data for Firebase
        student_data = {
            'student_id': student_id,
            'full_name': name,
            'course': course,
            'license_number': license_num,
            'plate_number': plate_num,
            'enrolled_date': current_time,
            'last_updated': current_time
        }
        
        # 3. Try to sync to Firebase (online) or queue (offline)
        if is_online():
            try:
                firebase_db.collection(COLLECTIONS['students']).document(str(student_id)).set({
                    **student_data,
                    'synced_at': firestore.SERVER_TIMESTAMP
                }, timeout=5)
                print(f"🔥 Student synced instantly: {name}")
            except Exception as e:
                print(f"⚠️  Instant sync failed, queuing: {e}")
                queue_manager.add_to_queue('students', str(student_id), student_data)
        else:
            print(f"📴 Offline - Student queued for sync: {name}")
            queue_manager.add_to_queue('students', str(student_id), student_data)
        
        print(f"✅ Student added: {name}")
        return True
        
    except Exception as e:
        print(f"❌ Error adding student: {e}")
        return False

# =================== STATUS FUNCTIONS ===================

def get_status():
    """Get current sync status and queue info"""
    online = is_online()
    queue_size = queue_manager.get_queue_size()
    
    print("\n🔥 FIREBASE SYNC STATUS")
    print("=" * 30)
    
    if online:
        print("🌐 Status: ONLINE - Firebase sync active")
    else:
        print("📴 Status: OFFLINE - Queuing syncs for later")
    
    if queue_size > 0:
        print(f"📋 Queue: {queue_size} items waiting to sync")
    else:
        print("✅ Queue: All synced up!")
    
    print(f"📊 Project: {FIREBASE_PROJECT_ID}")
    print(f"⏰ Last check: {datetime.now().strftime('%H:%M:%S')}")
    
    return {
        'online': online,
        'queue_size': queue_size,
        'project_id': FIREBASE_PROJECT_ID
    }

def force_sync():
    """Force sync all queued items (if online)"""
    if is_online():
        return queue_manager.process_queue(firebase_db)
    else:
        print("❌ Cannot force sync - no internet connection")
        return False

# =================== INITIALIZATION ===================

# Initialize Firebase when module is imported
init_firebase()

# Start queue manager
queue_manager.start_background_sync(lambda: firebase_db if firebase_ready else None)
