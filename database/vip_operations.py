# database/vip_operations.py - VIP Database Operations with Guard Tracking

import sqlite3
from datetime import datetime
import os

try:
    from etc.firebase.sync import is_online, firebase_db, COLLECTIONS, queue_manager
    firebase_available = True
except ImportError:
    firebase_available = False
    
VIP_DB_PATH = "database/motorpass.db"

def init_vip_database():
    """Initialize VIP table in main database with guard info columns"""
    try:
        os.makedirs(os.path.dirname(VIP_DB_PATH), exist_ok=True)
        
        conn = sqlite3.connect(VIP_DB_PATH)
        cursor = conn.cursor()
        
        # Check if table exists and get its structure
        cursor.execute("PRAGMA table_info(vip_records)")
        existing_columns = [column[1] for column in cursor.fetchall()]
        
        # Create table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vip_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plate_number TEXT NOT NULL,
                purpose TEXT NOT NULL,
                time_in TIMESTAMP NOT NULL,
                time_out TIMESTAMP,
                status TEXT DEFAULT 'IN' CHECK(status IN ('IN', 'OUT'))
            )
        ''')
        
        # Add new guard columns if they don't exist
        if 'guard_in_name' not in existing_columns:
            cursor.execute('ALTER TABLE vip_records ADD COLUMN guard_in_name TEXT')
        
        if 'guard_in_slot' not in existing_columns:
            cursor.execute('ALTER TABLE vip_records ADD COLUMN guard_in_slot TEXT')
        
        if 'guard_in_fingerprint_id' not in existing_columns:
            cursor.execute('ALTER TABLE vip_records ADD COLUMN guard_in_fingerprint_id TEXT')
        
        if 'guard_out_name' not in existing_columns:
            cursor.execute('ALTER TABLE vip_records ADD COLUMN guard_out_name TEXT')
        
        if 'guard_out_slot' not in existing_columns:
            cursor.execute('ALTER TABLE vip_records ADD COLUMN guard_out_slot TEXT')
        
        if 'guard_out_fingerprint_id' not in existing_columns:
            cursor.execute('ALTER TABLE vip_records ADD COLUMN guard_out_fingerprint_id TEXT')
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database init error: {e}")
        return False

def record_vip_time_in(plate_number, purpose):
    """Record TIME IN with purpose and sync to Firebase (original function)"""
    try:
        init_vip_database()
        
        # Double check not already IN
        if check_vip_status(plate_number)['found']:
            return {
                'success': False,
                'message': f"'{plate_number}' is already timed in!"
            }
        
        # 1. ALWAYS save to local database first
        conn = sqlite3.connect(VIP_DB_PATH)
        cursor = conn.cursor()
        
        now = datetime.now()
        cursor.execute('''
            INSERT INTO vip_records (plate_number, purpose, time_in, status)
            VALUES (?, ?, ?, 'IN')
        ''', (plate_number, purpose, now))
        
        vip_record_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # 2. Prepare data for Firebase sync
        current_time = now.isoformat()
        vip_data = {
            'id': vip_record_id,
            'plate_number': plate_number,
            'purpose': purpose,
            'time_in': current_time,
            'time_out': None,
            'status': 'IN'
        }
        
        # 3. Try to sync to Firebase (online) or queue (offline)
        if firebase_available:
            if is_online():
                try:
                    from firebase_admin import firestore
                    firebase_db.collection('vip_records').document(str(vip_record_id)).set({
                        **vip_data,
                        'synced_at': firestore.SERVER_TIMESTAMP
                    })
                    print(f"🔥 VIP TIME IN synced instantly: {plate_number}")
                except Exception as e:
                    print(f"⚠️  Instant sync failed, queuing: {e}")
                    queue_manager.add_to_queue('vip_records', str(vip_record_id), vip_data)
            else:
                print(f"📴 Offline - VIP TIME IN queued: {plate_number}")
                queue_manager.add_to_queue('vip_records', str(vip_record_id), vip_data)
        
        return {
            'success': True,
            'message': f"TIME IN: {plate_number}",
            'timestamp': now.strftime('%H:%M:%S')
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f"Database error: {str(e)}"
        }

def record_vip_time_in_with_guard(plate_number, purpose, guard_info):
    """Record TIME IN with purpose and guard fingerprint information"""
    try:
        init_vip_database()
        
        # Double check not already IN
        if check_vip_status(plate_number)['found']:
            return {
                'success': False,
                'message': f"'{plate_number}' is already timed in!"
            }
        
        # 1. ALWAYS save to local database first with guard info
        conn = sqlite3.connect(VIP_DB_PATH)
        cursor = conn.cursor()
        
        now = datetime.now()
        cursor.execute('''
            INSERT INTO vip_records (
                plate_number, purpose, time_in, status,
                guard_in_name, guard_in_slot, guard_in_fingerprint_id
            )
            VALUES (?, ?, ?, 'IN', ?, ?, ?)
        ''', (
            plate_number, purpose, now,
            guard_info.get('name'),
            guard_info.get('slot'),
            guard_info.get('fingerprint_id')
        ))
        
        vip_record_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # 2. Prepare data for Firebase sync
        current_time = now.isoformat()
        vip_data = {
            'id': vip_record_id,
            'plate_number': plate_number,
            'purpose': purpose,
            'time_in': current_time,
            'time_out': None,
            'status': 'IN',
            'guard_in_name': guard_info.get('name'),
            'guard_in_slot': guard_info.get('slot'),
            'guard_in_fingerprint_id': guard_info.get('fingerprint_id')
        }
        
        # 3. Try to sync to Firebase (online) or queue (offline)
        if firebase_available:
            if is_online():
                try:
                    from firebase_admin import firestore
                    firebase_db.collection('vip_records').document(str(vip_record_id)).set({
                        **vip_data,
                        'synced_at': firestore.SERVER_TIMESTAMP
                    })
                    print(f"🔥 VIP TIME IN synced instantly: {plate_number} (Guard: {guard_info.get('name')})")
                except Exception as e:
                    print(f"⚠️  Instant sync failed, queuing: {e}")
                    queue_manager.add_to_queue('vip_records', str(vip_record_id), vip_data)
            else:
                print(f"📴 Offline - VIP TIME IN queued: {plate_number} (Guard: {guard_info.get('name')})")
                queue_manager.add_to_queue('vip_records', str(vip_record_id), vip_data)
        
        return {
            'success': True,
            'message': f"TIME IN: {plate_number}",
            'timestamp': now.strftime('%H:%M:%S'),
            'guard': guard_info.get('name')
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f"Database error: {str(e)}"
        }

def record_vip_time_out(plate_number):
    """Record TIME OUT and sync to Firebase (original function)"""
    try:
        init_vip_database()
        
        # Check if exists and currently IN
        vip_status = check_vip_status(plate_number)
        if not vip_status['found']:
            return {
                'success': False,
                'message': f"'{plate_number}' is not currently timed in!"
            }
        
        # 1. Update local database
        conn = sqlite3.connect(VIP_DB_PATH)
        cursor = conn.cursor()
        
        now = datetime.now()
        cursor.execute('''
            UPDATE vip_records 
            SET time_out = ?, status = 'OUT'
            WHERE plate_number = ? 
            AND status = 'IN'
        ''', (now, plate_number))
        
        # Get the record ID for Firebase sync
        cursor.execute('''
            SELECT id FROM vip_records 
            WHERE plate_number = ? 
            AND time_out = ?
            AND status = 'OUT'
        ''', (plate_number, now))
        
        result = cursor.fetchone()
        if result:
            vip_record_id = result[0]
        else:
            conn.close()
            return {
                'success': False,
                'message': f"Failed to retrieve record ID for {plate_number}"
            }
        
        conn.commit()
        conn.close()
        
        # 2. Prepare data for Firebase sync
        current_time = now.isoformat()
        vip_data = {
            'id': vip_record_id,
            'plate_number': plate_number,
            'time_out': current_time,
            'status': 'OUT'
        }
        
        # 3. Try to sync to Firebase (online) or queue (offline)
        if firebase_available:
            if is_online():
                try:
                    from firebase_admin import firestore
                    firebase_db.collection('vip_records').document(str(vip_record_id)).update({
                        **vip_data,
                        'synced_at': firestore.SERVER_TIMESTAMP
                    })
                    print(f"🔥 VIP TIME OUT synced instantly: {plate_number}")
                except Exception as e:
                    print(f"⚠️  Instant sync failed, queuing: {e}")
                    queue_manager.add_to_queue('vip_records', str(vip_record_id), vip_data)
            else:
                print(f"📴 Offline - VIP TIME OUT queued: {plate_number}")
                queue_manager.add_to_queue('vip_records', str(vip_record_id), vip_data)
        
        return {
            'success': True,
            'message': f"TIME OUT: {plate_number}",
            'timestamp': now.strftime('%H:%M:%S')
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f"Database error: {str(e)}"
        }

def record_vip_time_out_with_guard(plate_number, guard_info):
    """Record TIME OUT with guard fingerprint information"""
    try:
        init_vip_database()
        
        # Check if exists and currently IN
        vip_status = check_vip_status(plate_number)
        if not vip_status['found']:
            return {
                'success': False,
                'message': f"'{plate_number}' is not currently timed in!"
            }
        
        # 1. Update local database with guard info
        conn = sqlite3.connect(VIP_DB_PATH)
        cursor = conn.cursor()
        
        now = datetime.now()
        cursor.execute('''
            UPDATE vip_records 
            SET time_out = ?, status = 'OUT',
                guard_out_name = ?, guard_out_slot = ?, guard_out_fingerprint_id = ?
            WHERE plate_number = ? 
            AND status = 'IN'
        ''', (
            now,
            guard_info.get('name'),
            guard_info.get('slot'),
            guard_info.get('fingerprint_id'),
            plate_number
        ))
        
        # Get the record ID for Firebase sync
        cursor.execute('''
            SELECT id FROM vip_records 
            WHERE plate_number = ? 
            AND time_out = ?
            AND status = 'OUT'
        ''', (plate_number, now))
        
        result = cursor.fetchone()
        if result:
            vip_record_id = result[0]
        else:
            conn.close()
            return {
                'success': False,
                'message': f"Failed to retrieve record ID for {plate_number}"
            }
        
        conn.commit()
        conn.close()
        
        # 2. Prepare data for Firebase sync
        current_time = now.isoformat()
        vip_data = {
            'id': vip_record_id,
            'plate_number': plate_number,
            'time_out': current_time,
            'status': 'OUT',
            'guard_out_name': guard_info.get('name'),
            'guard_out_slot': guard_info.get('slot'),
            'guard_out_fingerprint_id': guard_info.get('fingerprint_id')
        }
        
        # 3. Try to sync to Firebase (online) or queue (offline)
        if firebase_available:
            if is_online():
                try:
                    from firebase_admin import firestore
                    firebase_db.collection('vip_records').document(str(vip_record_id)).update({
                        **vip_data,
                        'synced_at': firestore.SERVER_TIMESTAMP
                    })
                    print(f"🔥 VIP TIME OUT synced instantly: {plate_number} (Guard: {guard_info.get('name')})")
                except Exception as e:
                    print(f"⚠️  Instant sync failed, queuing: {e}")
                    queue_manager.add_to_queue('vip_records', str(vip_record_id), vip_data)
            else:
                print(f"📴 Offline - VIP TIME OUT queued: {plate_number} (Guard: {guard_info.get('name')})")
                queue_manager.add_to_queue('vip_records', str(vip_record_id), vip_data)
        
        return {
            'success': True,
            'message': f"TIME OUT: {plate_number}",
            'timestamp': now.strftime('%H:%M:%S'),
            'guard': guard_info.get('name')
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f"Database error: {str(e)}"
        }

def check_vip_status(plate_number):
    """Check if plate number is currently IN"""
    try:
        conn = sqlite3.connect(VIP_DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT purpose, time_in FROM vip_records 
            WHERE plate_number = ? AND status = 'IN'
            ORDER BY time_in DESC LIMIT 1
        ''', (plate_number,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'found': True,
                'purpose': result[0],
                'time_in': result[1]
            }
        
        return {'found': False}
        
    except Exception as e:
        print(f"❌ Status check error: {e}")
        return {'found': False}

def get_all_vip_records(status=None):
    """Get all VIP records, optionally filtered by status"""
    try:
        conn = sqlite3.connect(VIP_DB_PATH)
        cursor = conn.cursor()
        
        if status:
            cursor.execute('''
                SELECT * FROM vip_records 
                WHERE status = ?
                ORDER BY time_in DESC
            ''', (status,))
        else:
            cursor.execute('''
                SELECT * FROM vip_records 
                ORDER BY time_in DESC
            ''')
        
        records = cursor.fetchall()
        conn.close()
        
        return records
        
    except Exception as e:
        print(f"❌ Error fetching VIP records: {e}")
        return []

def get_vip_stats():
    """Get VIP statistics"""
    try:
        conn = sqlite3.connect(VIP_DB_PATH)
        cursor = conn.cursor()
        
        # Count currently IN
        cursor.execute("SELECT COUNT(*) FROM vip_records WHERE status = 'IN'")
        currently_in = cursor.fetchone()[0]
        
        # Count total today
        cursor.execute("""
            SELECT COUNT(*) FROM vip_records 
            WHERE DATE(time_in) = DATE('now')
        """)
        today_total = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'current_in': currently_in,  # Fixed key name to match main_window.py
            'today_total': today_total
        }
        
    except Exception as e:
        print(f"❌ Error getting VIP stats: {e}")
        return {
            'currently_in': 0,
            'today_total': 0
        }
