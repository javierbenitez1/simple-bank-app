"""Creates the admin (username 'admin'), or upgrades an existing user to admin.
Usage: python -m app.create_admin "Full Name" email password"""
import sys

from app.dependencies import user_service
from app.services.exceptions import ConflictError, NotFoundError

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print('Usage: python -m app.create_admin "Full Name" email password')
        sys.exit(1)
    name, email, password = sys.argv[1:]
    try:
        if user_service.user_repo.find_by_email(email):
            admin = user_service.promote_to_admin(email, password)
            print(f"Updated existing user #{admin.user_id} to ADMIN")
        else:
            admin = user_service.create_user(name, email, password, role="ADMIN", username="admin")
            print(f"Admin created: #{admin.user_id}")
        print("Log in with username: admin")
    except (ConflictError, NotFoundError) as e:
        print(e)
        sys.exit(1)
