#!/usr/bin/env python3
"""
MotorPass Database Migration: SQLite to Firebase Firestore
Migrates all data from motorpass.db to Firebase Firestore
"""

import sqlite3
import os
import sys
import json
from datetime import datetime
from typing import Dict, List, Optional

# Firebase imports (install with: pip install firebase-admin)
try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    firebase_available = True
except ImportError:
    print("❌ Firebase Admin SDK not found!")
    print("📦 Install with: pip install firebase-admin")
    firebase_available = False
    sys.exit(1)

# =================== CONFIGURATION ===================

# **IMPORTANT: UPDATE THESE SETTINGS FOR YOUR PROJECT!**
FIREBASE_CONFIG = {
    'project_id': 'motorpass-456a0',  # Change to your Firebase project ID
    'credentials_file': 'json_folder/firebase_credentials.json'  # Path to your credentials JSON
}

# SQLite database path
SQLITE_DB_PATH = 'database/motorpass.db'

# Firestore collection names
COLLECTIONS = {
    'students': 'students',
    'staff': 'staff', 
    'guests': 'guests',
    'time_tracking': 'time_tracking',
    'current_status': 'current_status',
    'admins': 'admins'
}

# =================== FIREBASE SETUP ===================

def initialize_firebase():
    """Initialize Firebase connection"""
    try:
        # Check if credentials file exists
        if not os.path.exists(FIREBASE_CONFIG['credentials_file']):
            print(f"❌ Firebase credentials not found: {FIREBASE_CONFIG['credentials_file']}")
            print("💡 Download your service account key from Firebase Console:")
            print("   1. Go to Firebase Console > Project Settings > Service Accounts")
            print("   2. Click 'Generate New Private Key'")
            print("   3. Save as firebase_credentials.json")
            return None
        
        # Clear any existing Firebase apps
        if firebase_admin._apps:
            firebase_admin._apps.clear()
        
        # Initialize Firebase
        cred = credentials.Certificate(FIREBASE_CONFIG['credentials_file'])
        firebase_admin.initialize_app(cred, {
            'projectId': FIREBASE_CONFIG['project_id']
        })
        
        db = firestore.client()
        print("✅ Firebase initialized successfully")
        return db
        
    except Exception as e:
        print(f"❌ Firebase initialization failed: {e}")
        return None

# =================== DATA MIGRATION FUNCTIONS ===================

def migrate_students(sqlite_conn, firestore_db) -> bool:
    """Migrate students data"""
    try:
        print("👨‍🎓 Migrating students...")
        
        cursor = sqlite_conn.cursor()
        cursor.execute('''
            SELECT student_id, full_name, course, license_number, 
                   license_expiration, plate_number, fingerprint_slot,
                   enrolled_date, last_updated
            FROM students
        ''')
        
        students = cursor.fetchall()
        batch = firestore_db.batch()
        count = 0
        
        for row in students:
            student_data = {
                'student_id': row[0],
                'full_name': row[1],
                'course': row[2],
                'license_number': row[3],
                'license_expiration': row[4],
                'plate_number': row[5],
                'fingerprint_slot': row[6],
                'enrolled_date': row[7],
                'last_updated': row[8],
                'migrated_at': firestore.SERVER_TIMESTAMP,
                'user_type': 'STUDENT'
            }
            
            # Remove None values
            student_data = {k: v for k, v in student_data.items() if v is not None}
            
            doc_ref = firestore_db.collection(COLLECTIONS['students']).document(row[0])
            batch.set(doc_ref, student_data)
            count += 1
            
            # Commit batch every 500 documents (Firestore limit)
            if count % 500 == 0:
                batch.commit()
                batch = firestore_db.batch()
                print(f"  📝 Migrated {count} students...")
        
        # Commit remaining documents
        if count % 500 != 0:
            batch.commit()
        
        print(f"✅ Students migrated: {count} records")
        return True
        
    except Exception as e:
        print(f"❌ Error migrating students: {e}")
        return False

def migrate_staff(sqlite_conn, firestore_db) -> bool:
    """Migrate staff data"""
    try:
        print("👨‍💼 Migrating staff...")
        
        cursor = sqlite_conn.cursor()
        cursor.execute('''
            SELECT staff_no, full_name, staff_role, license_number,
                   license_expiration, plate_number, fingerprint_slot,
                   enrolled_date, last_updated
            FROM staff
        ''')
        
        staff = cursor.fetchall()
        batch = firestore_db.batch()
        count = 0
        
        for row in staff:
            staff_data = {
                'staff_no': row[0],
                'full_name': row[1],
                'staff_role': row[2],
                'license_number': row[3],
                'license_expiration': row[4],
                'plate_number': row[5],
                'fingerprint_slot': row[6],
                'enrolled_date': row[7],
                'last_updated': row[8],
                'migrated_at': firestore.SERVER_TIMESTAMP,
                'user_type': 'STAFF'
            }
            
            # Remove None values
            staff_data = {k: v for k, v in staff_data.items() if v is not None}
            
            doc_ref = firestore_db.collection(COLLECTIONS['staff']).document(row[0])
            batch.set(doc_ref, staff_data)
            count += 1
            
            if count % 500 == 0:
                batch.commit()
                batch = firestore_db.batch()
                print(f"  📝 Migrated {count} staff...")
        
        if count % 500 != 0:
            batch.commit()
        
        print(f"✅ Staff migrated: {count} records")
        return True
        
    except Exception as e:
        print(f"❌ Error migrating staff: {e}")
        return False

def migrate_guests(sqlite_conn, firestore_db) -> bool:
    """Migrate guests data"""
    try:
        print("👥 Migrating guests...")
        
        cursor = sqlite_conn.cursor()
        cursor.execute('''
            SELECT guest_id, full_name, plate_number, office_visiting, created_date
            FROM guests
        ''')
        
        guests = cursor.fetchall()
        batch = firestore_db.batch()
        count = 0
        
        for row in guests:
            guest_data = {
                'guest_id': row[0],
                'full_name': row[1],
                'plate_number': row[2],
                'office_visiting': row[3],
                'created_date': row[4],
                'migrated_at': firestore.SERVER_TIMESTAMP,
                'user_type': 'GUEST'
            }
            
            # Remove None values
            guest_data = {k: v for k, v in guest_data.items() if v is not None}
            
            doc_ref = firestore_db.collection(COLLECTIONS['guests']).document(str(row[0]))
            batch.set(doc_ref, guest_data)
            count += 1
            
            if count % 500 == 0:
                batch.commit()
                batch = firestore_db.batch()
                print(f"  📝 Migrated {count} guests...")
        
        if count % 500 != 0:
            batch.commit()
        
        print(f"✅ Guests migrated: {count} records")
        return True
        
    except Exception as e:
        print(f"❌ Error migrating guests: {e}")
        return False

def migrate_time_tracking(sqlite_conn, firestore_db) -> bool:
    """Migrate time tracking data"""
    try:
        print("⏰ Migrating time tracking...")
        
        cursor = sqlite_conn.cursor()
        cursor.execute('''
            SELECT id, user_id, user_name, user_type, action, 
                   timestamp, date, time
            FROM time_tracking
            ORDER BY timestamp DESC
        ''')
        
        records = cursor.fetchall()
        batch = firestore_db.batch()
        count = 0
        
        for row in records:
            time_data = {
                'id': row[0],
                'user_id': row[1],
                'user_name': row[2],
                'user_type': row[3],
                'action': row[4],
                'timestamp': row[5],
                'date': row[6],
                'time': row[7],
                'migrated_at': firestore.SERVER_TIMESTAMP
            }
            
            # Remove None values
            time_data = {k: v for k, v in time_data.items() if v is not None}
            
            doc_ref = firestore_db.collection(COLLECTIONS['time_tracking']).document(str(row[0]))
            batch.set(doc_ref, time_data)
            count += 1
            
            if count % 500 == 0:
                batch.commit()
                batch = firestore_db.batch()
                print(f"  📝 Migrated {count} time records...")
        
        if count % 500 != 0:
            batch.commit()
        
        print(f"✅ Time tracking migrated: {count} records")
        return True
        
    except Exception as e:
        print(f"❌ Error migrating time tracking: {e}")
        return False

def migrate_current_status(sqlite_conn, firestore_db) -> bool:
    """Migrate current status data"""
    try:
        print("📊 Migrating current status...")
        
        cursor = sqlite_conn.cursor()
        cursor.execute('''
            SELECT user_id, user_name, user_type, status, last_action_time
            FROM current_status
        ''')
        
        statuses = cursor.fetchall()
        batch = firestore_db.batch()
        count = 0
        
        for row in statuses:
            status_data = {
                'user_id': row[0],
                'user_name': row[1],
                'user_type': row[2],
                'status': row[3],
                'last_action_time': row[4],
                'migrated_at': firestore.SERVER_TIMESTAMP
            }
            
            # Remove None values  
            status_data = {k: v for k, v in status_data.items() if v is not None}
            
            doc_ref = firestore_db.collection(COLLECTIONS['current_status']).document(row[0])
            batch.set(doc_ref, status_data)
            count += 1
        
        if count > 0:
            batch.commit()
        
        print(f"✅ Current status migrated: {count} records")
        return True
        
    except Exception as e:
        print(f"❌ Error migrating current status: {e}")
        return False

def migrate_admins(sqlite_conn, firestore_db) -> bool:
    """Migrate admin data (optional)"""
    try:
        print("👑 Migrating admins...")
        
        cursor = sqlite_conn.cursor()
        cursor.execute('''
            SELECT admin_id, username, full_name, email, role,
                   fingerprint_slot, created_date, last_login, is_active
            FROM admins
        ''')
        
        admins = cursor.fetchall()
        batch = firestore_db.batch()
        count = 0
        
        for row in admins:
            admin_data = {
                'admin_id': row[0],
                'username': row[1],
                'full_name': row[2],
                'email': row[3],
                'role': row[4],
                'fingerprint_slot': row[5],
                'created_date': row[6],
                'last_login': row[7],
                'is_active': bool(row[8]),
                'migrated_at': firestore.SERVER_TIMESTAMP
                # Note: password_hash and salt are intentionally NOT migrated for security
            }
            
            # Remove None values
            admin_data = {k: v for k, v in admin_data.items() if v is not None}
            
            doc_ref = firestore_db.collection(COLLECTIONS['admins']).document(str(row[0]))
            batch.set(doc_ref, admin_data)
            count += 1
        
        if count > 0:
            batch.commit()
        
        print(f"✅ Admins migrated: {count} records")
        print("⚠️  Note: Password hashes were not migrated for security")
        return True
        
    except Exception as e:
        print(f"❌ Error migrating admins: {e}")
        return False

# =================== VERIFICATION FUNCTIONS ===================

def verify_migration(sqlite_conn, firestore_db) -> bool:
    """Verify migration by comparing counts"""
    try:
        print("\n🔍 Verifying migration...")
        print("=" * 50)
        
        cursor = sqlite_conn.cursor()
        verification_passed = True
        
        # Check each table
        tables_to_check = [
            ('students', COLLECTIONS['students']),
            ('staff', COLLECTIONS['staff']),
            ('guests', COLLECTIONS['guests']),
            ('time_tracking', COLLECTIONS['time_tracking']),
            ('current_status', COLLECTIONS['current_status']),
            ('admins', COLLECTIONS['admins'])
        ]
        
        for sqlite_table, firestore_collection in tables_to_check:
            # Get SQLite count
            cursor.execute(f"SELECT COUNT(*) FROM {sqlite_table}")
            sqlite_count = cursor.fetchone()[0]
            
            # Get Firestore count
            firestore_count = len(list(firestore_db.collection(firestore_collection).stream()))
            
            status = "✅" if sqlite_count == firestore_count else "❌"
            print(f"{status} {sqlite_table}: SQLite({sqlite_count}) → Firestore({firestore_count})")
            
            if sqlite_count != firestore_count:
                verification_passed = False
        
        print("=" * 50)
        if verification_passed:
            print("✅ Migration verification PASSED!")
        else:
            print("❌ Migration verification FAILED!")
        
        return verification_passed
        
    except Exception as e:
        print(f"❌ Error during verification: {e}")
        return False

def create_firestore_indexes(firestore_db):
    """Create indexes for better performance (info only - manual setup required)"""
    print("\n📋 Recommended Firestore indexes to create manually:")
    print("=" * 60)
    print("Go to Firebase Console > Firestore > Indexes and create these:")
    print()
    
    indexes = [
        {
            'collection': 'time_tracking',
            'fields': [('user_id', 'Ascending'), ('timestamp', 'Descending')],
            'description': 'Query user time history'
        },
        {
            'collection': 'time_tracking', 
            'fields': [('date', 'Descending'), ('user_type', 'Ascending')],
            'description': 'Daily reports by user type'
        },
        {
            'collection': 'current_status',
            'fields': [('status', 'Ascending'), ('user_type', 'Ascending')],
            'description': 'Current users by type and status'
        },
        {
            'collection': 'students',
            'fields': [('full_name', 'Ascending')],
            'description': 'Search students by name'
        },
        {
            'collection': 'staff',
            'fields': [('full_name', 'Ascending')],
            'description': 'Search staff by name'
        },
        {
            'collection': 'guests',
            'fields': [('plate_number', 'Ascending')],
            'description': 'Search guests by plate'
        }
    ]
    
    for idx in indexes:
        print(f"Collection: {idx['collection']}")
        print(f"Fields: {idx['fields']}")
        print(f"Purpose: {idx['description']}")
        print()

# =================== MAIN MIGRATION FUNCTION ===================

def main():
    """Main migration function"""
    print("🚀 MotorPass Migration: SQLite → Firebase Firestore")
    print("=" * 70)
    
    # Check if SQLite database exists
    if not os.path.exists(SQLITE_DB_PATH):
        print(f"❌ SQLite database not found: {SQLITE_DB_PATH}")
        return False
    
    # Initialize Firebase
    firestore_db = initialize_firebase()
    if not firestore_db:
        return False
    
    # Connect to SQLite
    try:
        sqlite_conn = sqlite3.connect(SQLITE_DB_PATH)
        print(f"✅ Connected to SQLite: {SQLITE_DB_PATH}")
    except Exception as e:
        print(f"❌ Failed to connect to SQLite: {e}")
        return False
    
    # Perform migration
    migration_steps = [
        migrate_students,
        migrate_staff, 
        migrate_guests,
        migrate_time_tracking,
        migrate_current_status,
        migrate_admins
    ]
    
    print(f"\n🔄 Starting migration of {len(migration_steps)} tables...")
    print("-" * 50)
    
    success_count = 0
    for step in migration_steps:
        if step(sqlite_conn, firestore_db):
            success_count += 1
        else:
            print("⚠️  Some data might not have migrated correctly")
    
    # Verify migration
    verification_passed = verify_migration(sqlite_conn, firestore_db)
    
    # Create indexes info
    create_firestore_indexes(firestore_db)
    
    # Clean up
    sqlite_conn.close()
    
    # Final summary
    print("\n🎉 Migration Summary:")
    print("=" * 30)
    print(f"Tables migrated: {success_count}/{len(migration_steps)}")
    print(f"Verification: {'PASSED' if verification_passed else 'FAILED'}")
    print(f"Firebase Project: {FIREBASE_CONFIG['project_id']}")
    
    if success_count == len(migration_steps) and verification_passed:
        print("\n✅ Migration completed successfully!")
        print("🔥 Your data is now in Firebase Firestore!")
        print("\n📋 Next steps:")
        print("1. Update your app to use Firestore instead of SQLite")
        print("2. Create the recommended indexes in Firebase Console")
        print("3. Set up Firestore security rules")
        print("4. Test your application with the new database")
    else:
        print("\n❌ Migration completed with issues!")
        print("Please check the errors above and retry if needed.")
    
    return success_count == len(migration_steps) and verification_passed

if __name__ == "__main__":
    main()
