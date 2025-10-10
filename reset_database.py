#!/usr/bin/env python3
# reset_database.py - Reinitialize the database

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.init_database import initialize_all_databases
from database.office_operation import create_office_table

def main():
    print("=" * 60)
    print("🔧 MOTORPASS DATABASE INITIALIZATION")
    print("=" * 60)
    
    # Initialize all tables
    print("\n📊 Creating all database tables...")
    initialize_all_databases()
    
    # Create offices table
    print("\n🏢 Creating office management table...")
    create_office_table()
    
    print("\n" + "=" * 60)
    print("✅ Database initialization complete!")
    print("=" * 60)
    print("\n📝 Tables created:")
    print("   ✓ admins")
    print("   ✓ students")
    print("   ✓ staff")
    print("   ✓ guests")
    print("   ✓ time_tracking")
    print("   ✓ expired_license_attempts")
    print("   ✓ current_status")
    print("   ✓ offices (with default offices)")
    print("\nYou can now use the system normally!")

if __name__ == "__main__":
    main()

