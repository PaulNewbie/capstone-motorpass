# etc/utils/json_database.py - Centralized JSON Database Operations

import json
import os

# Import file paths from config
from config import (
    FINGERPRINT_DATA_FILE,
    ADMIN_DATA_FILE, 
    ADMIN_ROLES_FILE
)

from database.db_operations import (
    get_user_by_id,
    get_student_by_id,
    get_staff_by_id
)

# =================== FINGERPRINT DATABASE FUNCTIONS ===================

def load_fingerprint_database():
    """Load fingerprint database"""
    if os.path.exists(FINGERPRINT_DATA_FILE):
        try:
            with open(FINGERPRINT_DATA_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_fingerprint_database(database):
    """Save fingerprint database"""
    os.makedirs(os.path.dirname(FINGERPRINT_DATA_FILE), exist_ok=True)
    with open(FINGERPRINT_DATA_FILE, 'w') as f:
        json.dump(database, f, indent=4)

# =================== ADMIN DATABASE FUNCTIONS ===================

def load_admin_database():
    """Load admin database"""
    if os.path.exists(ADMIN_DATA_FILE):
        try:
            with open(ADMIN_DATA_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_admin_database(database):
    """Save admin database"""
    os.makedirs(os.path.dirname(ADMIN_DATA_FILE), exist_ok=True)
    with open(ADMIN_DATA_FILE, 'w') as f:
        json.dump(database, f, indent=4)
        
# =================== ADMIN ROLES DATABASE FUNCTIONS ===================

def load_admin_roles():
    """Load admin roles database"""
    if os.path.exists(ADMIN_ROLES_FILE):
        try:
            with open(ADMIN_ROLES_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_admin_roles(roles_db):
    """Save admin roles database"""
    os.makedirs(os.path.dirname(ADMIN_ROLES_FILE), exist_ok=True)
    with open(ADMIN_ROLES_FILE, 'w') as f:
        json.dump(roles_db, f, indent=4)
        
# =================== DATABASE COMPATIBILITY FUNCTIONS ===================

def safe_get_student_by_id(student_id):
    """Safely get student by ID with fallback"""
    try:
        return get_student_by_id(student_id)
    except:
        try:
            result = get_user_by_id(student_id)
            if result and result.get('user_type') == 'STUDENT':
                return result
        except:
            pass
        return None

def safe_get_staff_by_id(staff_id):
    """Safely get staff by ID with fallback"""
    try:
        return get_staff_by_id(staff_id)
    except:
        try:
            result = get_user_by_id(staff_id)
            if result and result.get('user_type') == 'STAFF':
                return result
        except:
            pass
        return None
