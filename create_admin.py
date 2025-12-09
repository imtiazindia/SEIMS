"""
Script to create the first admin user for SEIMS
Run this after setting up your database: python create_admin.py
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from src.database.connection import get_db_session
from src.database.models import User
from src.auth.authenticator import get_password_hash

def create_admin_user():
    """Create the first admin user"""
    
    print("=" * 60)
    print("SEIMS - Admin User Creation")
    print("=" * 60)
    
    # Get admin details
    print("\nEnter admin user details:")
    admin_email = input("Email (default: admin@seims.edu): ").strip() or "admin@seims.edu"
    admin_name = input("Name (default: System Administrator): ").strip() or "System Administrator"
    admin_password = input("Password (min 8 characters): ").strip()
    
    if not admin_password or len(admin_password) < 8:
        print("❌ Password must be at least 8 characters long!")
        return
    
    if not admin_password:
        print("❌ Password cannot be empty!")
        return
    
    print("\n⏳ Creating admin user...")
    
    try:
        with get_db_session() as session:
            # Check if admin already exists
            existing = session.query(User).filter(User.email == admin_email).first()
            if existing:
                print(f"⚠️  User with email '{admin_email}' already exists!")
                response = input("Do you want to update the password? (y/n): ").strip().lower()
                if response == 'y':
                    existing.password_hash = get_password_hash(admin_password)
                    existing.is_active = True
                    session.commit()
                    print("✅ Admin password updated!")
                else:
                    print("❌ Cancelled.")
                return
            
            # Create new admin user
            admin = User(
                email=admin_email,
                password_hash=get_password_hash(admin_password),
                name=admin_name,
                role="admin",
                is_active=True
            )
            session.add(admin)
            session.commit()
            
            print("\n" + "=" * 60)
            print("✅ Admin user created successfully!")
            print("=" * 60)
            print(f"Email: {admin_email}")
            print(f"Name: {admin_name}")
            print(f"Role: admin")
            print("=" * 60)
            print("\n⚠️  IMPORTANT: Save these credentials securely!")
            print("⚠️  Change the password after first login for security.")
            print("=" * 60)
            
    except Exception as e:
        print(f"\n❌ Error creating admin user: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Check that DATABASE_URL is set correctly")
        print("2. Verify database is accessible")
        print("3. Ensure migrations have been run (alembic upgrade head)")
        print("4. Check database connection in .env file")

if __name__ == "__main__":
    try:
        create_admin_user()
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")

