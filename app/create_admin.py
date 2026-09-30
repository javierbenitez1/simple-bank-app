"""Creates an admin user. Usage: python -m app.create_admin "Full Name" email password"""
import sys

from app.dependencies import user_service
from app.services.exceptions import ConflictError

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print('Usage: python -m app.create_admin "Full Name" email password')
        sys.exit(1)
    name, email, password = sys.argv[1:]
    try:
        admin = user_service.create_user(name, email, password, role="ADMIN")
        print(f"Admin created: #{admin.user_id} {admin.email}")
    except ConflictError as e:
        print(e)
        sys.exit(1)
