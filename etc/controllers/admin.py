# controllers/admin.py - CLEANED UP with admin enrollment functions

from config import ADMIN_MENU
from etc.services.hardware.fingerprint import *

from database.db_operations import (
    get_all_time_records,
    clear_all_time_records,
    get_students_currently_in,
    get_database_stats,
)

from etc.utils.display_helpers import (
    display_menu, 
    get_user_input, 
    confirm_action, 
    display_separator
)

# Import from utils - NO MORE DUPLICATES!
from etc.utils.json_database import (
    load_admin_database, 
    save_admin_database,
    load_admin_roles,
    save_admin_roles,
    load_fingerprint_database,
    save_fingerprint_database
)

from etc.controllers.auth.fingerprint_admin import (
    enroll_super_admin, 
    check_admin_fingerprint_exists, 
    enroll_guard_admin,
    enroll_finger_with_user_info,
    get_user_id_gui
)

import time
import json
import os


# Legacy function for compatibility
def enroll_admin_fingerprint():
    """Legacy function - redirects to enroll_super_admin"""
    return enroll_super_admin()

# =================== SLOT MANAGEMENT FUNCTIONS ===================

def find_next_available_slot():
    """Automatically find the next available slot (skips slots 1-2 for admins)"""
    try:
        # Read current templates from sensor
        if finger.read_templates() != adafruit_fingerprint.OK:
            print("❌ Failed to read sensor templates")
            return None
        
        # Load fingerprint database
        database = load_fingerprint_database()
        
        # Find next available slot starting from 3 (skip admin slots 1-2)
        for slot in range(3, finger.library_size + 1):
            if str(slot) not in database:
                print(f"🎯 Auto-assigned slot: #{slot}")
                return slot
        
        print("❌ No available slots found")
        return None
        
    except Exception as e:
        print(f"❌ Error finding available slot: {e}")
        return None

# =================== ADMIN FUNCTIONS ===================

def admin_enroll():
    """Enroll new user (student or staff)"""
    if finger.read_templates() != adafruit_fingerprint.OK:
        print("❌ Failed to read templates")
        return
    
    print(f"📊 Current enrollments: {finger.template_count}")

    # Get slot (skip admin slots 1-2)
    location = find_next_available_slot()
    if location in [1, 2]:
        print("❌ Slots #1-2 reserved for admins. Use slot 3+")
        return
    
    success = enroll_finger_with_user_info(location)  
    print(f"{'✅ Success!' if success else '❌ Failed.'}")

def admin_view_enrolled():
    """Display all enrolled users (students and staff)"""
    database = load_fingerprint_database()
    if not database:
        print("📁 No users enrolled.")
        return
    
    print("\n👥 ENROLLED USERS:")
    display_separator()
    
    student_count = 0
    staff_count = 0
    admin_count = 0
    
    for finger_id, info in database.items():
        user_type = info.get('user_type', 'STUDENT')
        
        # Count users by type
        if user_type == 'STUDENT':
            student_count += 1
        elif user_type == 'STAFF':
            staff_count += 1
        elif user_type in ['GUARD_ADMIN']:
            admin_count += 1
            
        # Skip admin slots for regular listing
        if finger_id in ["1", "2"] and user_type in ['GUARD_ADMIN']:
            continue
        
        print(f"🆔 Slot: {finger_id}")
        print(f"👤 Name: {info['name']}")
        print(f"👥 Type: {user_type}")
        
        if user_type == 'STUDENT':
            print(f"🎓 Student ID: {info.get('student_id', 'N/A')}")
            print(f"📚 Course: {info.get('course', 'N/A')}")
        elif user_type == 'STAFF':
            print(f"👔 Staff No.: {info.get('staff_no', 'N/A')}")
            print(f"💼 Role: {info.get('staff_role', 'N/A')}")
        
        print(f"🪪 License: {info.get('license_number', 'N/A')}")
        print(f"📅 License Exp: {info.get('license_expiration', 'N/A')}")
        print(f"🏍️ Plate: {info.get('plate_number', 'N/A')}")
        print(f"🕒 Enrolled: {info.get('enrolled_date', 'Unknown')}")
        print("-" * 50)
    
    total_count = student_count + staff_count
    if total_count == 0:
        print("📁 No regular users enrolled.")
    else:
        print(f"\n📊 Total Users: {total_count}")
        print(f"   🎓 Students: {student_count}")
        print(f"   👔 Staff: {staff_count}")
        print(f"   🛡️ Admins: {admin_count}")

def admin_view_admins():
    """View all admin accounts"""
    print("\n👥 ADMIN ACCOUNTS")
    print("=" * 50)
    
    try:
        admin_db = load_admin_database()
        fingerprint_db = load_fingerprint_database()
        
        if not admin_db and "2" not in fingerprint_db:
            print("📭 No admin accounts found.")
            return
        
        # Show super admin (slot 1)
        if "1" in admin_db:
            info = admin_db["1"]
            name = info.get('name', 'Unknown')
            enrolled_date = info.get('enrolled_date', 'Unknown')
            print(f"👑 Slot #1: {name} (Super Admin)")
            print(f"   Enrolled: {enrolled_date}")
            print()
        
        # Show guard admin (slot 2)
        if "2" in fingerprint_db:
            info = fingerprint_db["2"]
            name = info.get('name', 'Unknown')
            enrolled_date = info.get('enrolled_date', 'Unknown')
            print(f"🛡️ Slot #2: {name} (Guard Admin)")
            print(f"   Enrolled: {enrolled_date}")
            print()
        
        # Show any other admin slots
        for slot_id, info in admin_db.items():
            if slot_id not in ["1", "2"]:
                role = info.get('role', 'admin')
                name = info.get('name', 'Unknown')
                enrolled_date = info.get('enrolled_date', 'Unknown')
                print(f"🔧 Slot #{slot_id}: {name} ({role.title()})")
                print(f"   Enrolled: {enrolled_date}")
                print()
        
    except Exception as e:
        print(f"❌ Error loading admin accounts: {e}")

def admin_delete_fingerprint(slot_id=None):
    """Delete user fingerprint"""
    database = load_fingerprint_database()
    if not database:
        print("📁 No users enrolled.")
        return
    
    if not slot_id:
        admin_view_enrolled()
        
        try:
            slot_id = get_user_input("Enter Slot ID to delete")
        except:
            print("❌ Cancelled.")
            return
    
    # Convert to string for database check
    slot_id_str = str(slot_id)
    
    if slot_id_str == "1":
        print("❌ Cannot delete super admin slot. Use 'Change Admin' option.")
        return
    elif slot_id_str == "2":
        print("❌ Cannot delete guard admin slot. Use admin management.")
        return
        
    # Check if exists in database
    if slot_id_str in database:
        user_info = database[slot_id_str]
        user_type = user_info.get('user_type', 'STUDENT')
        user_id = user_info.get('student_id' if user_type == 'STUDENT' else 'staff_no', 'N/A')
        print(f"\n📋 Deleting: {user_info['name']} ({user_type} - ID: {user_id})")
    else:
        print(f"\n📋 Deleting slot {slot_id} (not in database)")
    
    try:
        # Delete from sensor (convert to int)
        if finger.delete_model(int(slot_id)) == 0:  # 0 = success
            print("✅ Deleted from sensor")
            
            # Delete from database if exists
            if slot_id_str in database:
                del database[slot_id_str]
                save_fingerprint_database(database)
                print("✅ Deleted from database")
            
            print(f"🎉 Slot {slot_id} deleted successfully!")
        else:
            print("❌ Failed to delete from sensor.")
    except Exception as e:
        print(f"❌ Error: {e}")

def admin_reset_all():
    """Reset all system data with confirmation"""
    if not confirm_action("Delete ALL student/staff fingerprints?", dangerous=True):
        print("❌ Cancelled.")
        return
        
    if input("⚠️ Type 'DELETE ALL' to confirm: ").strip() != 'DELETE ALL':
        print("❌ Cancelled.")
        return
    
    try:
        database = load_fingerprint_database()
        
        # Delete all student/staff fingerprints (preserve admin slots 1-2)
        for slot_id in list(database.keys()):
            if slot_id not in ["1", "2"]:
                finger.delete_model(int(slot_id))
        
        # Keep only admin slots
        admin_only_db = {k: v for k, v in database.items() if k in ["1", "2"]}
        save_fingerprint_database(admin_only_db)
        print("✅ All student/staff data reset. Admins preserved.")
        
    except Exception as e:
        print(f"❌ Reset error: {e}")

def admin_change_fingerprint():
    """Change admin fingerprint (hidden option)"""
    print("\n🔄 CHANGE ADMIN FINGERPRINT")
    print("⚠️  This will replace the current admin fingerprint")
    
    if not confirm_action("Replace admin fingerprint?", dangerous=True):
        print("❌ Cancelled.")
        return
    
    if enroll_super_admin():
        print("✅ Admin fingerprint changed!")
    else:
        print("❌ Failed to change.")

# =================== SYNC AND OTHER FUNCTIONS ===================

def admin_sync_database():
    """Sync database from Google Sheets - saves directly to motorpass.db"""
    # ... (keep existing sync function as is)
    try:
        import gspread
        from oauth2client.service_account import ServiceAccountCredentials
        import sqlite3
        from datetime import datetime
        
        print("🔄 Starting database sync from Google Sheets...")
        
        # Google Sheets authentication
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name("json_folder/spreadsheet_credentials.json", scope)
        client = gspread.authorize(creds)
        
        # Open the spreadsheet
        sheet_name = "MotorPass Registration Form (Responses)"
        print(f"📊 Connecting to '{sheet_name}'...")
        
        sheet = client.open(sheet_name).sheet1
        rows = sheet.get_all_records()
        
        print(f"📋 Found {len(rows)} records in Google Sheets")
        
        # Connect to motorpass.db
        conn = sqlite3.connect("database/motorpass.db")
        cursor = conn.cursor()
        
        students_added = 0
        staff_added = 0
        errors = 0
        
        print("💾 Saving to motorpass.db...")
        
        for row in rows:
            try:
                # Extract data from row
                full_name = row.get('Full Name', '').strip()
                license_number = str(row.get('License Number', '')).strip()
                expiration_date = row.get('License Expiration Date', '').strip()
                plate_number = row.get('Plate Number of the Motorcycle', '').strip()
                course = row.get('Course', '').strip()
                student_id = row.get('Student No.', '').strip()
                staff_role = row.get('Staff Role', '').strip()
                staff_no = str(row.get('Staff No.', '')).strip()
                
                # Skip if no name
                if not full_name:
                    continue
                
                # Determine if student or staff
                if student_id and not staff_no:
                    # It's a student
                    cursor.execute('''
                        INSERT OR REPLACE INTO students 
                        (student_id, full_name, course, license_number, 
                         license_expiration, plate_number, last_updated)
                        VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    ''', (student_id, full_name, course, license_number, 
                          expiration_date, plate_number))
                    students_added += 1
                    
                elif staff_no and not student_id:
                    # It's a staff member
                    cursor.execute('''
                        INSERT OR REPLACE INTO staff 
                        (staff_no, full_name, staff_role, license_number, 
                         license_expiration, plate_number, last_updated)
                        VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    ''', (staff_no, full_name, staff_role, license_number, 
                          expiration_date, plate_number))
                    staff_added += 1
                    
                elif student_id and staff_no:
                    # Both filled - handle as student by default
                    print(f"⚠️ Both Student No. and Staff No. filled for {full_name}, treating as student")
                    cursor.execute('''
                        INSERT OR REPLACE INTO students 
                        (student_id, full_name, course, license_number, 
                         license_expiration, plate_number, last_updated)
                        VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    ''', (student_id, full_name, course, license_number, 
                          expiration_date, plate_number))
                    students_added += 1
                else:
                    # Neither student nor staff ID
                    print(f"⚠️ Skipping {full_name} - No Student No. or Staff No.")
                    errors += 1
                    
            except Exception as e:
                print(f"❌ Error processing row for {row.get('Full Name', 'Unknown')}: {e}")
                errors += 1
        
        # Commit all changes
        conn.commit()
        
        # Get final counts
        cursor.execute('SELECT COUNT(*) FROM students')
        total_students = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM staff')
        total_staff = cursor.fetchone()[0]
        
        conn.close()
        
        print("\n✅ Database sync completed!")
        print(f"📊 Sync Results:")
        print(f"   🎓 Students added/updated: {students_added}")
        print(f"   👔 Staff added/updated: {staff_added}")
        if errors > 0:
            print(f"   ❌ Errors: {errors}")
        
        print(f"\n📊 Database Totals:")
        print(f"   🎓 Total Students: {total_students}")
        print(f"   👔 Total Staff: {total_staff}")
            
    except gspread.exceptions.SpreadsheetNotFound:
        print(f"❌ Spreadsheet '{sheet_name}' not found")
        print("💡 Please check:")
        print("   1. The exact name of your Google Sheet")
        print("   2. That the service account has access to the sheet")
        print("   3. The sheet is shared with the service account email")
        
    except FileNotFoundError:
        print("❌ credentials.json not found!")
        print("💡 Please ensure json_folder/spreadsheet_credentials.json exists")
        
    except Exception as e:
        print(f"❌ Sync failed: {e}")
        print("💡 Check your credentials.json and internet connection")

def admin_view_time_records():
    """View all time records with user type information"""
    records = get_all_time_records()
    if not records:
        print("📁 No time records.")
        return
    
    print("\n🕒 TIME RECORDS:")
    display_separator()
    
    for record in records:
        status_icon = "🟢" if record['status'] == 'IN' else "🔴"
        user_type_icon = "🎓" if record.get('user_type', 'STUDENT') == 'STUDENT' else "👔"
        
        print(f"{status_icon} {user_type_icon} {record['student_name']} ({record['student_id']})")
        print(f"   📅 {record['date']} 🕒 {record['time']} 📊 {record['status']}")
        print("-" * 50)

def admin_clear_time_records():
    """Clear all time records"""
    if not confirm_action("Clear ALL time records?", dangerous=True):
        print("❌ Cancelled.")
        return
    
    try:
        if clear_all_time_records():
            print("✅ All time records cleared.")
        else:
            print("❌ Failed to clear records.")
    except Exception as e:
        print(f"❌ Error: {e}")

# =================== MAIN ADMIN PANEL ===================

def admin_panel(main_window=None):
    """Admin panel with role-based access control"""
    print("\n🔧 ADMIN PANEL")
    
    # Check admin fingerprint exists
    if not check_admin_fingerprint_exists():
        print("\n🔐 NO SUPER ADMIN FINGERPRINT FOUND!")
        if input("Setup super admin fingerprint? (y/N): ").lower() != 'y':
            return
        if not enroll_super_admin():
            print("❌ Setup failed.")
            return
        print("✅ Super admin setup complete!")
    
    # Role-based authentication
    print("\n🔐 Opening authentication...")
    
    try:
        from etc.services.hardware.fingerprint import authenticate_admin_with_role
        
        user_role = authenticate_admin_with_role(main_window=main_window)
        
        if not user_role:
            print("❌ Authentication failed!")
            return
        
        print(f"✅ Authenticated as: {user_role}")
        
        # HIDE MAIN WINDOW AFTER SUCCESSFUL AUTHENTICATION (Admin behavior)
        if main_window:
            print("🔐 Hiding main window for admin panel...")
            main_window.withdraw()
        
    except Exception as e:
        print(f"❌ Authentication Error: {e}")
        return
    
    try:
        from etc.ui.admin_gui import AdminPanelGUI
        
        admin_functions = {
            'authenticate': lambda: True,
            'enroll': admin_enroll,
            'view_users': admin_view_enrolled,
            'delete_fingerprint': admin_delete_fingerprint,
            'sync': admin_sync_database,
            'get_time_records': get_all_time_records,
            'clear_records': admin_clear_time_records,
            'get_stats': get_database_stats,
            'change_admin': admin_change_fingerprint,
            'reset': admin_reset_all,
            'view_admins': admin_view_admins,
            'enroll_guard': enroll_guard_admin
        }
        
        # Create admin panel with role (fullscreen)
        gui = AdminPanelGUI(admin_functions, skip_auth=True, user_role=user_role)
        gui.run()
        
    except Exception as e:
        print(f"❌ Admin panel error: {e}")
    finally:
        # Always restore main window when admin panel closes
        if main_window:
            print("🔄 Restoring main window...")
            main_window.deiconify()
    
    print("👋 Admin panel closed")
