"""
Script to create an admin user
Usage: python create_admin.py
"""
import sys
from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.user import User


def create_admin_user():
    """Create an admin user if it doesn't exist"""
    db = SessionLocal()

    try:
        # Check if admin user exists
        admin = db.query(User).filter(User.username == "admin").first()

        if admin:
            print("Admin user already exists!")
            return

        # Create admin user
        admin = User(
            username="admin",
            email="admin@cantieretrack.com",
            full_name="Administrator",
            hashed_password=get_password_hash("admin123"),
            is_active=True,
            is_superuser=True
        )

        db.add(admin)
        db.commit()

        print("Admin user created successfully!")
        print("Username: admin")
        print("Password: admin123")
        print("\nPlease change the password after first login!")

    except Exception as e:
        print(f"Error creating admin user: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    create_admin_user()
