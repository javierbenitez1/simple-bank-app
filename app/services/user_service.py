from app.models.entities import User
from app.repositories.user_repository import UserRepository
from app.services.exceptions import ConflictError, NotFoundError


class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def create_user(self, name: str, email: str) -> User:
        if self.user_repo.find_by_email(email):
            raise ConflictError(f"A user with email {email} already exists")
        return self.user_repo.save(name.strip(), email.strip())

    def get_user(self, user_id: int) -> User:
        user = self.user_repo.find_by_id(user_id)
        if user is None:
            raise NotFoundError(f"User {user_id} not found")
        return user