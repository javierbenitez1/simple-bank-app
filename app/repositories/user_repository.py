import re
from typing import Optional

from app.database import get_db, next_id, reset_counter
from app.models.entities import User


def _to_user(doc) -> User:
    return User(
        user_id=doc["_id"],
        name=doc["name"],
        email=doc["email"],
        created_at=doc["created_at"],
    )


class UserRepository:
    @property
    def collection(self):
        return get_db().users

    def save(self, name: str, email: str) -> User:
        user = User(user_id=next_id("users"), name=name, email=email)
        self.collection.insert_one({
            "_id": user.user_id,
            "name": user.name,
            "email": user.email,
            "created_at": user.created_at,
        })
        return user

    def find_by_id(self, user_id: int) -> Optional[User]:
        doc = self.collection.find_one({"_id": user_id})
        return _to_user(doc) if doc else None

    def find_by_email(self, email: str) -> Optional[User]:
        pattern = f"^{re.escape(email)}$"
        doc = self.collection.find_one({"email": {"$regex": pattern, "$options": "i"}})
        return _to_user(doc) if doc else None

    def clear(self):
        self.collection.delete_many({})
        reset_counter("users")
