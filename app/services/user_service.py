from app.models.entities import User
from app.repositories.account_repository import AccountRepository
from app.repositories.user_repository import UserRepository
from app.security import hash_password, verify_password
from app.services.exceptions import ConflictError, ForbiddenError, NotFoundError, UnauthorizedError

# Only the administrator can have these usernames
RESERVED_USERNAMES = {"admin"}


class UserService:
    def __init__(self, user_repo: UserRepository, account_repo: AccountRepository):
        self.user_repo = user_repo
        self.account_repo = account_repo

    def create_user(
        self, name: str, email: str, password: str, role: str = "CUSTOMER", username: str | None = None
    ) -> User:
        if username is not None:
            username = username.strip().lower()
            if username in RESERVED_USERNAMES and role != "ADMIN":
                raise ForbiddenError(f"The username '{username}' is reserved for the administrator")
            if self.user_repo.find_by_username(username):
                raise ConflictError(f"The username {username} is already taken")
        if self.user_repo.find_by_email(email):
            raise ConflictError(f"A user with email {email} already exists")
        return self.user_repo.save(name.strip(), email.strip(), hash_password(password), role, username)

    def authenticate(self, identifier: str, password: str) -> User:
        """Log in with a username, or with an email (anything containing @)."""
        identifier = identifier.strip()
        if "@" in identifier:
            user = self.user_repo.find_by_email(identifier)
        else:
            user = self.user_repo.find_by_username(identifier)
        # Same message either way, so attackers can't tell which accounts exist
        if user is None or not verify_password(password, user.password_hash):
            raise UnauthorizedError("Incorrect username or password")
        return user

    def promote_to_admin(self, email: str, password: str) -> User:
        """Turns an existing user into THE admin, with the username 'admin'."""
        user = self.user_repo.find_by_email(email)
        if user is None:
            raise NotFoundError(f"No user with email {email}")
        current_admin = self.user_repo.find_by_username("admin")
        if current_admin and current_admin.user_id != user.user_id:
            raise ConflictError("Another user already has the username 'admin'")
        self.user_repo.make_admin(user.user_id, "admin", hash_password(password))
        return self.get_user(user.user_id)

    def list_users(self) -> list[User]:
        return self.user_repo.find_all()

    def get_user(self, user_id: int) -> User:
        user = self.user_repo.find_by_id(user_id)
        if user is None:
            raise NotFoundError(f"User {user_id} not found")
        return user

    def update_user(self, user_id: int, name: str | None, email: str | None) -> User:
        user = self.get_user(user_id)
        if email is not None:
            existing = self.user_repo.find_by_email(email)
            if existing and existing.user_id != user_id:
                raise ConflictError(f"A user with email {email} already exists")
            user.email = email.strip()
        if name is not None:
            user.name = name.strip()
        return self.user_repo.update(user)

    def delete_user(self, user_id: int) -> None:
        self.get_user(user_id)
        if self.account_repo.find_by_user_id(user_id):
            raise ConflictError(
                f"User {user_id} still has open accounts. Close them before deleting the user."
            )
        self.user_repo.delete(user_id)
