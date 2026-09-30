from app.models.entities import User
from app.repositories.account_repository import AccountRepository
from app.repositories.user_repository import UserRepository
from app.security import hash_password, verify_password
from app.services.exceptions import ConflictError, NotFoundError, UnauthorizedError


class UserService:
    def __init__(self, user_repo: UserRepository, account_repo: AccountRepository):
        self.user_repo = user_repo
        self.account_repo = account_repo

    def create_user(self, name: str, email: str, password: str, role: str = "CUSTOMER") -> User:
        if self.user_repo.find_by_email(email):
            raise ConflictError(f"A user with email {email} already exists")
        return self.user_repo.save(name.strip(), email.strip(), hash_password(password), role)

    def authenticate(self, email: str, password: str) -> User:
        user = self.user_repo.find_by_email(email)
        # Same message either way, so attackers can't tell which emails exist
        if user is None or not verify_password(password, user.password_hash):
            raise UnauthorizedError("Incorrect email or password")
        return user

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
