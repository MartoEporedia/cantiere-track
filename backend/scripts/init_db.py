#!/usr/bin/env python3
"""
Database initialization script

Creates database tables and optionally creates an admin user
"""
import sys
import os

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import engine, SessionLocal, Base
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.employee import Employee
from app.models.site import Site
from app.models.attendance import Attendance
from app.models.audit_log import AuditLog
import getpass


def create_tables():
    """Create all database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Tables created successfully")


def create_admin_user():
    """Create an admin user interactively"""
    db = SessionLocal()

    try:
        print("\n=== Create Admin User ===")

        # Check if admin already exists
        existing_admin = db.query(User).filter(User.role == UserRole.ADMIN).first()
        if existing_admin:
            print(f"⚠ Admin user already exists: {existing_admin.username}")
            response = input("Create another admin user? (y/N): ").lower()
            if response != 'y':
                return

        # Get admin details
        username = input("Admin username: ").strip()
        if not username:
            print("✗ Username cannot be empty")
            return

        # Check if username exists
        existing = db.query(User).filter(User.username == username).first()
        if existing:
            print(f"✗ Username '{username}' already exists")
            return

        email = input("Admin email: ").strip()
        if not email:
            print("✗ Email cannot be empty")
            return

        # Check if email exists
        existing_email = db.query(User).filter(User.email == email).first()
        if existing_email:
            print(f"✗ Email '{email}' already exists")
            return

        full_name = input("Full name (optional): ").strip() or None

        # Get password securely
        while True:
            password = getpass.getpass("Password (min 8 chars, 1 uppercase, 1 digit): ")
            if len(password) < 8:
                print("✗ Password must be at least 8 characters")
                continue
            if not any(c.isupper() for c in password):
                print("✗ Password must contain at least one uppercase letter")
                continue
            if not any(c.isdigit() for c in password):
                print("✗ Password must contain at least one digit")
                continue

            password_confirm = getpass.getpass("Confirm password: ")
            if password != password_confirm:
                print("✗ Passwords do not match")
                continue
            break

        # Create admin user
        hashed_password = get_password_hash(password)
        admin_user = User(
            username=username,
            email=email,
            full_name=full_name,
            hashed_password=hashed_password,
            role=UserRole.ADMIN,
            is_superuser=True,
            is_active=True
        )

        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)

        print(f"\n✓ Admin user '{username}' created successfully")
        print(f"  Email: {email}")
        print(f"  Role: {admin_user.role.value}")

    except Exception as e:
        print(f"✗ Error creating admin user: {e}")
        db.rollback()
    finally:
        db.close()


def show_stats():
    """Show database statistics"""
    db = SessionLocal()

    try:
        print("\n=== Database Statistics ===")

        user_count = db.query(User).count()
        admin_count = db.query(User).filter(User.role == UserRole.ADMIN).count()
        manager_count = db.query(User).filter(User.role == UserRole.MANAGER).count()
        viewer_count = db.query(User).filter(User.role == UserRole.VIEWER).count()

        employee_count = db.query(Employee).count()
        site_count = db.query(Site).count()
        attendance_count = db.query(Attendance).count()
        audit_count = db.query(AuditLog).count()

        print(f"Users: {user_count} (Admin: {admin_count}, Manager: {manager_count}, Viewer: {viewer_count})")
        print(f"Employees: {employee_count}")
        print(f"Sites: {site_count}")
        print(f"Attendance records: {attendance_count}")
        print(f"Audit logs: {audit_count}")

    except Exception as e:
        print(f"Error retrieving stats: {e}")
    finally:
        db.close()


def main():
    """Main initialization function"""
    print("=" * 50)
    print("CantiereTrack Database Initialization")
    print("=" * 50)

    # Create tables
    create_tables()

    # Show current stats
    show_stats()

    # Ask to create admin
    print("\n")
    response = input("Create admin user? (Y/n): ").lower()
    if response != 'n':
        create_admin_user()

    # Show final stats
    show_stats()

    print("\n✓ Initialization complete!")


if __name__ == "__main__":
    main()
