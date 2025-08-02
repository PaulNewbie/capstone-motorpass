# database/vip_operations.py - VIP Database Operations

import sqlite3
from datetime import datetime
import os

# Database path - adjust according to your project structure
VIP_DB_PATH = "databases/motorpass_main.db"

def init_vip_database():
    """Initialize VIP table in database"""
    try:
        # Ensure database directory exists
        os.makedirs(os.path.dirname(VIP_DB_PATH), exist_ok=True)
        
        conn = sqlite3.connect(VIP_DB_PATH)
        cursor = conn.cursor()
        
        # Create VIP records table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vip_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plate_number TEXT NOT NULL,
                purpose TEXT NOT NULL,
                time_in_date DATE NOT NULL,
                time_in_time TIME NOT NULL,
                time_in_timestamp TIMESTAMP NOT NULL,
                time_out_date DATE,
                time_out_time TIME,
                time_out_timestamp TIMESTAMP,
                status TEXT DEFAULT 'IN' CHECK(status IN ('IN', 'OUT'))
            )
        ''')
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error initializing VIP database: {e}")
        return False

def record_vip_time_in(plate_number, purpose):
    """Record VIP time in to database"""
    try:
        # Initialize database if needed
        init_vip_database()
        
        conn = sqlite3.connect(VIP_DB_PATH)
        cursor = conn.cursor()
        
        # Check if already timed in
        cursor.execute('''
            SELECT COUNT(*) FROM vip_records 
            WHERE plate_number = ? AND status = 'IN'
        ''', (plate_number,))
        
        if cursor.fetchone()[0] > 0:
            conn.close()
            return {
                'success': False,
                'message': f"VIP with plate '{plate_number}' is already timed in!"
            }
        
        # Insert new VIP time in record
        now = datetime.now()
        cursor.execute('''
            INSERT INTO vip_records 
            (plate_number, purpose, time_in_date, time_in_time, time_in_timestamp, status)
            VALUES (?, ?, ?, ?, ?, 'IN')
        ''', (plate_number, purpose, now.date(), now.time(), now))
        
        conn.commit()
        conn.close()
        
        print(f"✅ VIP Time In recorded: {plate_number} - {purpose}")
        return {
            'success': True,
            'message': f"VIP Time In recorded for {plate_number}",
            'timestamp': now.strftime('%H:%M:%S')
        }
        
    except Exception as e:
        print(f"❌ Error recording VIP time in: {e}")
        return {
            'success': False,
            'message': f"Database error: {str(e)}"
        }

def check_vip_status(plate_number):
    """Check if VIP is currently timed in"""
    try:
        conn = sqlite3.connect(VIP_DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT purpose, time_in_time, time_in_date FROM vip_records 
            WHERE plate_number = ? AND status = 'IN'
            ORDER BY time_in_timestamp DESC LIMIT 1
        ''', (plate_number,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'found': True,
                'purpose': result[0],
                'time_in': result[1],
                'date_in': result[2]
            }
        
        return {'found': False}
        
    except Exception as e:
        print(f"❌ Error checking VIP status: {e}")
        return {'found': False, 'error': str(e)}

def record_vip_time_out(plate_number):
    """Record VIP time out"""
    try:
        conn = sqlite3.connect(VIP_DB_PATH)
        cursor = conn.cursor()
        
        # Check if VIP is currently timed in
        vip_status = check_vip_status(plate_number)
        if not vip_status['found']:
            conn.close()
            return {
                'success': False,
                'message': f"No VIP with plate '{plate_number}' is currently timed in!"
            }
        
        # Update the most recent IN record for this plate
        now = datetime.now()
        cursor.execute('''
            UPDATE vip_records 
            SET time_out_date = ?, time_out_time = ?, time_out_timestamp = ?, status = 'OUT'
            WHERE plate_number = ? AND status = 'IN'
            AND id = (
                SELECT id FROM vip_records 
                WHERE plate_number = ? AND status = 'IN'
                ORDER BY time_in_timestamp DESC LIMIT 1
            )
        ''', (now.date(), now.time(), now, plate_number, plate_number))
        
        if cursor.rowcount > 0:
            conn.commit()
            conn.close()
            print(f"✅ VIP Time Out recorded: {plate_number}")
            return {
                'success': True,
                'message': f"VIP Time Out recorded for {plate_number}",
                'timestamp': now.strftime('%H:%M:%S'),
                'vip_info': vip_status
            }
        else:
            conn.close()
            return {
                'success': False,
                'message': "Failed to update VIP record"
            }
        
    except Exception as e:
        print(f"❌ Error recording VIP time out: {e}")
        return {
            'success': False,
            'message': f"Database error: {str(e)}"
        }

def get_all_vip_records(status=None):
    """Get all VIP records, optionally filtered by status"""
    try:
        conn = sqlite3.connect(VIP_DB_PATH)
        cursor = conn.cursor()
        
        if status:
            cursor.execute('''
                SELECT * FROM vip_records 
                WHERE status = ?
                ORDER BY time_in_timestamp DESC
            ''', (status,))
        else:
            cursor.execute('''
                SELECT * FROM vip_records 
                ORDER BY time_in_timestamp DESC
            ''')
        
        records = cursor.fetchall()
        conn.close()
        
        return records
        
    except Exception as e:
        print(f"❌ Error getting VIP records: {e}")
        return []

def get_vip_stats():
    """Get VIP statistics"""
    try:
        conn = sqlite3.connect(VIP_DB_PATH)
        cursor = conn.cursor()
        
        # Total VIPs currently IN
        cursor.execute("SELECT COUNT(*) FROM vip_records WHERE status = 'IN'")
        current_in = cursor.fetchone()[0]
        
        # Total VIP visits today
        today = datetime.now().date()
        cursor.execute("SELECT COUNT(*) FROM vip_records WHERE time_in_date = ?", (today,))
        today_visits = cursor.fetchone()[0]
        
        # Total VIP records
        cursor.execute("SELECT COUNT(*) FROM vip_records")
        total_records = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'current_in': current_in,
            'today_visits': today_visits,
            'total_records': total_records
        }
        
    except Exception as e:
        print(f"❌ Error getting VIP stats: {e}")
        return {
            'current_in': 0,
            'today_visits': 0,
            'total_records': 0
        }
