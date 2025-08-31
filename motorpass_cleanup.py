#!/usr/bin/env python3
"""
MotorPass Database Cleanup Script
Cleans up messed up indexes in guests and time_tracking tables
while preserving data in other tables, and adds proper test data.
"""

import sqlite3
import os
from datetime import datetime, timedelta
import random

DATABASE_PATH = "database/motorpass.db"

def backup_database():
    """Create a backup of the current database"""
    backup_path = f"database/motorpass_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    try:
        import shutil
        shutil.copy2(DATABASE_PATH, backup_path)
        print(f"✅ Database backed up to: {backup_path}")
        return True
    except Exception as e:
        print(f"❌ Error creating backup: {e}")
        return False

def clean_time_tracking_table():
    """Clean up time_tracking table with proper indexes"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        print("🧹 Cleaning up time_tracking table...")
        
        # First, let's see what's currently in the table
        cursor.execute("SELECT COUNT(*) FROM time_tracking")
        current_count = cursor.fetchone()[0]
        print(f"Current time_tracking records: {current_count}")
        
        # Drop existing indexes if they exist
        cursor.execute("DROP INDEX IF EXISTS idx_time_tracking_user")
        cursor.execute("DROP INDEX IF EXISTS idx_time_tracking_date")
        
        # Clear corrupted data but keep table structure
        cursor.execute("DELETE FROM time_tracking")
        print("Cleared existing time_tracking data")
        
        # Recreate proper indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_time_tracking_user ON time_tracking(user_id, user_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_time_tracking_date ON time_tracking(date)')
        
        conn.commit()
        conn.close()
        print("✅ time_tracking table cleaned and reindexed")
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Error cleaning time_tracking table: {e}")
        return False

def clean_guests_table():
    """Clean up guests table with proper indexes"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        print("🧹 Cleaning up guests table...")
        
        # Check current guests data
        cursor.execute("SELECT COUNT(*) FROM guests")
        current_count = cursor.fetchone()[0]
        print(f"Current guests records: {current_count}")
        
        # Drop existing indexes if they exist
        cursor.execute("DROP INDEX IF EXISTS idx_guests_name")
        cursor.execute("DROP INDEX IF EXISTS idx_guests_plate")
        
        # Clear corrupted guest data
        cursor.execute("DELETE FROM guests")
        print("Cleared existing guests data")
        
        # Reset AUTO_INCREMENT
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='guests'")
        
        # Recreate proper indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_guests_name ON guests(full_name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_guests_plate ON guests(plate_number)')
        
        conn.commit()
        conn.close()
        print("✅ guests table cleaned and reindexed")
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Error cleaning guests table: {e}")
        return False

def add_sample_time_tracking():
    """Add proper time tracking data for existing students and staff"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        print("📝 Adding sample time tracking data...")
        
        # Get existing students
        cursor.execute("SELECT student_id, full_name FROM students LIMIT 5")
        students = cursor.fetchall()
        
        # Get existing staff
        cursor.execute("SELECT staff_no, full_name FROM staff LIMIT 3")
        staff = cursor.fetchall()
        
        # Generate time tracking for the past week
        for i in range(7):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            
            # Add student entries
            for student_id, full_name in students:
                if random.choice([True, False]):  # 50% chance of entry each day
                    # IN entry
                    in_time = f"{random.randint(7,9):02d}:{random.randint(0,59):02d}:00"
                    cursor.execute('''
                        INSERT INTO time_tracking (user_id, user_name, user_type, action, date, time, timestamp)
                        VALUES (?, ?, 'STUDENT', 'IN', ?, ?, ?)
                    ''', (student_id, full_name, date, in_time, f"{date} {in_time}"))
                    
                    # OUT entry (later in the day)
                    out_hour = random.randint(15, 18)
                    out_time = f"{out_hour:02d}:{random.randint(0,59):02d}:00"
                    cursor.execute('''
                        INSERT INTO time_tracking (user_id, user_name, user_type, action, date, time, timestamp)
                        VALUES (?, ?, 'STUDENT', 'OUT', ?, ?, ?)
                    ''', (student_id, full_name, date, out_time, f"{date} {out_time}"))
            
            # Add staff entries
            for staff_no, full_name in staff:
                if random.choice([True, True, False]):  # 66% chance of entry each day
                    # IN entry
                    in_time = f"{random.randint(8,9):02d}:{random.randint(0,59):02d}:00"
                    cursor.execute('''
                        INSERT INTO time_tracking (user_id, user_name, user_type, action, date, time, timestamp)
                        VALUES (?, ?, 'STAFF', 'IN', ?, ?, ?)
                    ''', (staff_no, full_name, date, in_time, f"{date} {in_time}"))
                    
                    # OUT entry
                    out_hour = random.randint(16, 19)
                    out_time = f"{out_hour:02d}:{random.randint(0,59):02d}:00"
                    cursor.execute('''
                        INSERT INTO time_tracking (user_id, user_name, user_type, action, date, time, timestamp)
                        VALUES (?, ?, 'STAFF', 'OUT', ?, ?, ?)
                    ''', (staff_no, full_name, date, out_time, f"{date} {out_time}"))
        
        conn.commit()
        conn.close()
        print("✅ Sample time tracking data added")
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Error adding time tracking data: {e}")
        return False

def add_new_guests():
    """Add 10 new proper guest users"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        print("👥 Adding 10 new guest users...")
        
        # Sample guest data
        guests_data = [
            ("John Smith", "ABC123", "CSS Department"),
            ("Maria Garcia", "XYZ789", "Administration Office"),
            ("David Lee", "DEF456", "Dean's Office"),
            ("Sarah Johnson", "GHI789", "Registrar"),
            ("Michael Brown", "JKL012", "IT Department"),
            ("Lisa Wilson", "MNO345", "Library"),
            ("Robert Taylor", "PQR678", "SDO Office"),
            ("Emma Davis", "STU901", "Main Office"),
            ("James Miller", "VWX234", "CSS Department"),
            ("Anna Rodriguez", "YZA567", "IT Department")
        ]
        
        for full_name, plate_number, office_visiting in guests_data:
            cursor.execute('''
                INSERT INTO guests (full_name, plate_number, office_visiting, created_date)
                VALUES (?, ?, ?, ?)
            ''', (full_name, plate_number, office_visiting, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        
        conn.commit()
        conn.close()
        print("✅ 10 new guest users added successfully")
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Error adding guest users: {e}")
        return False

def add_guest_time_tracking():
    """Add time tracking for some of the new guests"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        print("⏰ Adding time tracking for guests...")
        
        # Get the newly added guests
        cursor.execute("SELECT guest_id, full_name FROM guests ORDER BY guest_id DESC LIMIT 10")
        guests = cursor.fetchall()
        
        # Add time tracking for some guests (simulate visits)
        today = datetime.now().strftime('%Y-%m-%d')
        
        for i, (guest_id, full_name) in enumerate(guests[:5]):  # Only first 5 guests
            # IN entry
            in_time = f"{random.randint(9,11):02d}:{random.randint(0,59):02d}:00"
            cursor.execute('''
                INSERT INTO time_tracking (user_id, user_name, user_type, action, date, time, timestamp)
                VALUES (?, ?, 'GUEST', 'IN', ?, ?, ?)
            ''', (f"GUEST_{guest_id}", full_name, today, in_time, f"{today} {in_time}"))
            
            # Some guests have OUT entry too
            if i % 2 == 0:  # Every other guest
                out_hour = random.randint(14, 16)
                out_time = f"{out_hour:02d}:{random.randint(0,59):02d}:00"
                cursor.execute('''
                    INSERT INTO time_tracking (user_id, user_name, user_type, action, date, time, timestamp)
                    VALUES (?, ?, 'GUEST', 'OUT', ?, ?, ?)
                ''', (f"GUEST_{guest_id}", full_name, today, out_time, f"{today} {out_time}"))
        
        conn.commit()
        conn.close()
        print("✅ Guest time tracking added")
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Error adding guest time tracking: {e}")
        return False

def update_current_status():
    """Update current_status table based on latest time_tracking entries"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        print("🔄 Updating current status table...")
        
        # Clear existing current_status
        cursor.execute("DELETE FROM current_status")
        
        # Get latest action for each user
        cursor.execute('''
            WITH latest_actions AS (
                SELECT user_id, user_name, user_type, action,
                       ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY timestamp DESC) as rn
                FROM time_tracking
            )
            SELECT user_id, user_name, user_type, action
            FROM latest_actions
            WHERE rn = 1 AND action = 'IN'
        ''')
        
        current_users = cursor.fetchall()
        
        # Insert users who are currently IN
        for user_id, user_name, user_type, action in current_users:
            cursor.execute('''
                INSERT INTO current_status (user_id, user_name, user_type, status, last_action_time)
                VALUES (?, ?, ?, 'IN', ?)
            ''', (user_id, user_name, user_type, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        
        conn.commit()
        conn.close()
        print(f"✅ Current status updated - {len(current_users)} users currently IN")
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Error updating current status: {e}")
        return False

def verify_cleanup():
    """Verify the cleanup was successful"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        print("\n📊 Cleanup Verification:")
        print("=" * 50)
        
        # Check students
        cursor.execute("SELECT COUNT(*) FROM students")
        student_count = cursor.fetchone()[0]
        print(f"Students: {student_count}")
        
        # Check staff
        cursor.execute("SELECT COUNT(*) FROM staff")
        staff_count = cursor.fetchone()[0]
        print(f"Staff: {staff_count}")
        
        # Check guests
        cursor.execute("SELECT COUNT(*) FROM guests")
        guest_count = cursor.fetchone()[0]
        print(f"Guests: {guest_count}")
        
        # Check time tracking
        cursor.execute("SELECT COUNT(*) FROM time_tracking")
        tracking_count = cursor.fetchone()[0]
        print(f"Time tracking records: {tracking_count}")
        
        # Check current status
        cursor.execute("SELECT COUNT(*) FROM current_status")
        status_count = cursor.fetchone()[0]
        print(f"Currently IN: {status_count}")
        
        # Show sample of new guests
        print("\n👥 Sample of new guests:")
        cursor.execute("SELECT full_name, plate_number, office_visiting FROM guests LIMIT 5")
        for row in cursor.fetchall():
            print(f"  - {row[0]} ({row[1]}) visiting {row[2]}")
        
        # Show indexes
        print("\n🔍 Database indexes:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%'")
        indexes = cursor.fetchall()
        for idx in indexes:
            print(f"  - {idx[0]}")
        
        conn.close()
        print("\n✅ Database cleanup completed successfully!")
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Error verifying cleanup: {e}")
        return False

def main():
    """Main cleanup function"""
    print("🚀 MotorPass Database Cleanup Starting...")
    print("=" * 60)
    
    if not os.path.exists(DATABASE_PATH):
        print(f"❌ Database not found at: {DATABASE_PATH}")
        print("Please ensure the database file exists before running cleanup.")
        return
    
    # Step 1: Backup
    if not backup_database():
        print("❌ Backup failed. Aborting cleanup.")
        return
    
    # Step 2: Clean up tables
    if not clean_time_tracking_table():
        print("❌ Failed to clean time_tracking table")
        return
    
    if not clean_guests_table():
        print("❌ Failed to clean guests table")
        return
    
    # Step 3: Add new data
    if not add_sample_time_tracking():
        print("❌ Failed to add sample time tracking")
        return
    
    if not add_new_guests():
        print("❌ Failed to add new guests")
        return
    
    if not add_guest_time_tracking():
        print("❌ Failed to add guest time tracking")
        return
    
    # Step 4: Update current status
    if not update_current_status():
        print("❌ Failed to update current status")
        return
    
    # Step 5: Verify
    verify_cleanup()

if __name__ == "__main__":
    main()
