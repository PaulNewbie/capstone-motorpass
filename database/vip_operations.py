# database/vip_operations.py - SIMPLIFIED Database Operations

import sqlite3
from datetime import datetime
import os

VIP_DB_PATH = "database/motorpass.db"

def init_vip_database():
    """Initialize VIP table"""
    try:
        os.makedirs(os.path.dirname(VIP_DB_PATH), exist_ok=True)
        
        conn = sqlite3.connect(VIP_DB_PATH)
        cursor = conn.cursor()
        
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
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database init error: {e}")
        return False

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

def record_vip_time_in(plate_number, purpose):
    """Record TIME IN with purpose"""
    try:
        init_vip_database()
        
        # Double check not already IN
        if check_vip_status(plate_number)['found']:
            return {
                'success': False,
                'message': f"'{plate_number}' is already timed in!"
            }
        
        conn = sqlite3.connect(VIP_DB_PATH)
        cursor = conn.cursor()
        
        now = datetime.now()
        cursor.execute('''
            INSERT INTO vip_records (plate_number, purpose, time_in, status)
            VALUES (?, ?, ?, 'IN')
        ''', (plate_number, purpose, now))
        
        conn.commit()
        conn.close()
        
        return {
            'success': True,
            'message': f"TIME IN: {plate_number} - {purpose}",
            'timestamp': now.strftime('%H:%M:%S')
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f"Database error: {str(e)}"
        }

def record_vip_time_out(plate_number):
    """Record TIME OUT"""
    try:
        # Check if actually IN
        if not check_vip_status(plate_number)['found']:
            return {
                'success': False,
                'message': f"'{plate_number}' is not currently timed in!"
            }
        
        conn = sqlite3.connect(VIP_DB_PATH)
        cursor = conn.cursor()
        
        now = datetime.now()
        cursor.execute('''
            UPDATE vip_records 
            SET time_out = ?, status = 'OUT'
            WHERE plate_number = ? AND status = 'IN'
        ''', (now, plate_number))
        
        conn.commit()
        conn.close()
        
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
        cursor.execute('''
            SELECT COUNT(*) FROM vip_records 
            WHERE DATE(time_in) = ?
        ''', (today,))
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

def get_current_vip_list():
    """Get list of all VIPs currently IN"""
    try:
        conn = sqlite3.connect(VIP_DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT plate_number, purpose, time_in FROM vip_records 
            WHERE status = 'IN'
            ORDER BY time_in DESC
        ''')
        
        records = cursor.fetchall()
        conn.close()
        
        # Format the results
        vip_list = []
        for record in records:
            vip_list.append({
                'plate_number': record[0],
                'purpose': record[1],
                'time_in': record[2]
            })
        
        return vip_list
        
    except Exception as e:
        print(f"❌ Error getting current VIP list: {e}")
        return []
