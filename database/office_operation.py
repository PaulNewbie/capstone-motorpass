import sqlite3
from typing import List, Dict, Optional
import random
from database.init_database import MOTORPASS_DB

def create_office_table():
    """Create office table with default data - RUN THIS FIRST"""
    try:
        conn = sqlite3.connect(MOTORPASS_DB)
        cursor = conn.cursor()
        
        # Create offices table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS offices (
                office_id INTEGER PRIMARY KEY AUTOINCREMENT,
                office_name TEXT UNIQUE NOT NULL,
                office_code TEXT NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Insert default offices with 4-digit codes - UPDATED
        default_offices = [
            ("IT Department", "2481"),
            ("SDO Office", "5739"),
            ("Library", "6912"),
            ("Registrar", "3147"),
            ("CSS Department", "8275"),
            ("Dean's Office", "4593"),
            ("Cashier Office", "1368"),
            ("Main Office", "7054")
        ]
        
        for office_name, code in default_offices:
            cursor.execute('''
                INSERT OR IGNORE INTO offices (office_name, office_code)
                VALUES (?, ?)
            ''', (office_name, code))
        
        conn.commit()
        conn.close()
        print("✅ Office table created successfully with default offices!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating office table: {e}")
        return False

def get_all_offices() -> List[Dict]:
    """Get all active offices"""
    try:
        conn = sqlite3.connect(MOTORPASS_DB)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT office_id, office_name, office_code, is_active
            FROM offices 
            WHERE is_active = 1
            ORDER BY office_name
        ''')
        
        offices = []
        for row in cursor.fetchall():
            offices.append({
                'office_id': row[0],
                'office_name': row[1],
                'office_code': row[2],
                'is_active': row[3]
            })
        
        conn.close()
        return offices
        
    except sqlite3.Error as e:
        print(f"❌ Error fetching offices: {e}")
        return []

def verify_office_code(office_name: str, entered_code: str) -> bool:
    """Verify if entered code matches office code"""
    try:
        conn = sqlite3.connect(MOTORPASS_DB)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT office_code FROM offices 
            WHERE office_name = ?
            AND is_active = 1
        ''', (office_name,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return row[0] == entered_code.strip()
        return False
        
    except Exception as e:
        print(f"❌ Error verifying office code: {e}")
        return False

def add_office(office_name: str) -> bool:
    """Add new office with auto-generated 4-digit code"""
    try:
        conn = sqlite3.connect(MOTORPASS_DB)
        cursor = conn.cursor()
        
        # Generate unique 4-digit code - UPDATED
        while True:
            code = f"{random.randint(1000, 9999)}"
            cursor.execute('SELECT office_id FROM offices WHERE office_code = ?', (code,))
            if not cursor.fetchone():
                break
        
        cursor.execute('''
            INSERT INTO offices (office_name, office_code)
            VALUES (?, ?)
        ''', (office_name, code))
        
        conn.commit()
        conn.close()
        print(f"✅ Office '{office_name}' added with code {code}")
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Error adding office: {e}")
        return False

def update_office_code(office_name: str, new_code: str) -> bool:
    """Update office security code"""
    try:
        # UPDATED TO 4-DIGIT VALIDATION
        if not new_code.isdigit() or len(new_code) != 4:
            print("❌ Code must be exactly 4 digits")
            return False
        
        conn = sqlite3.connect(MOTORPASS_DB)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE offices 
            SET office_code = ?, last_updated = CURRENT_TIMESTAMP
            WHERE office_name = ?
        ''', (new_code, office_name))
        
        conn.commit()
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Error updating office code: {e}")
        return False

def delete_office(office_name: str) -> bool:
    """Soft delete office (set inactive)"""
    try:
        conn = sqlite3.connect(MOTORPASS_DB)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE offices 
            SET is_active = 0, last_updated = CURRENT_TIMESTAMP
            WHERE office_name = ?
        ''', (office_name,))
        
        conn.commit()
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Error deleting office: {e}")
        return False
