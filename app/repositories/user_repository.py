from typing import Optional

from app.models.entities import User


class UserRepository:
    def __init__(self):
        self._users: dict[int, User] = {}
        self._next_id = 1

    def save(self, name: str, email: str) -> User:
        user = User(user_id=self._next_id, name=name, email=email)
        self._users[user.user_id] = user
        self._next_id += 1
        return user

    def find_by_id(self, user_id: int) -> Optional[User]:
        return self._users.get(user_id)

    def find_by_email(self, email: str) -> Optional[User]:
        return next(
            (u for u in self._users.values() if u.email.lower() == email.lower()),
            None,
        )

    def clear(self):
        self._users.clear()
        self._next_id = 1