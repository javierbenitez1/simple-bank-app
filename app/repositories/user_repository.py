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
        password_hash=doc.get("password_hash"),
        role=doc.get("role", "CUSTOMER"),
        username=doc.get("username"),
        failed_login_attempts=doc.get("failed_login_attempts", 0),
        locked_until=_as_utc(doc.get("locked_until")),
    )


class UserRepository:
    @property
    def collection(self):
        return get_db().users

    def save(
        self,
        name: str,
        email: str,
        password_hash: str | None = None,
        role: str = "CUSTOMER",
        username: str | None = None,
    ) -> User:
        user = User(user_id=next_id("users"), name=name, email=email,
                    password_hash=password_hash, role=role, username=username)
        self.collection.insert_one({
            "_id": user.user_id,
            "name": user.name,
            "email": user.email,
            "username": user.username,
            "password_hash": user.password_hash,
            "role": user.role,
            "created_at": user.created_at,
        })
        return user

    def find_all(self) -> list[User]:
        return [_to_user(doc) for doc in self.collection.find().sort("_id", 1)]

    def find_by_id(self, user_id: int) -> Optional[User]:
        doc = self.collection.find_one({"_id": user_id})
        return _to_user(doc) if doc else None

    def find_by_email(self, email: str) -> Optional[User]:
        pattern = f"^{re.escape(email)}$"
        doc = self.collection.find_one({"email": {"$regex": pattern, "$options": "i"}})
        return _to_user(doc) if doc else None

    def find_by_username(self, username: str) -> Optional[User]:
        # Usernames are stored lowercase, so lookups are case-insensitive
        doc = self.collection.find_one({"username": username.strip().lower()})
        return _to_user(doc) if doc else None

    def update(self, user: User) -> User:
        self.collection.update_one(
            {"_id": user.user_id},
            {"$set": {"name": user.name, "email": user.email}},
        )
        return user

    def make_admin(self, user_id: int, username: str, password_hash: str) -> None:
        self.collection.update_one(
            {"_id": user_id},
            {"$set": {"role": "ADMIN", "username": username, "password_hash": password_hash}},
        )

    def delete(self, user_id: int) -> bool:
        return self.collection.delete_one({"_id": user_id}).deleted_count == 1

    def clear(self):
        self.collection.delete_many({})
        reset_counter("users")

    # ----- Login lockout -----

    def record_failed_login(self, user_id: int) -> int:
        """Adds 1 to the failed login counter and returns the new count."""
        from pymongo import ReturnDocument
        doc = self.collection.find_one_and_update(
            {"_id": user_id},
            {"$inc": {"failed_login_attempts": 1}},
            return_document=ReturnDocument.AFTER,
        )
        return doc["failed_login_attempts"]

    def lock(self, user_id: int, until) -> None:
        self.collection.update_one({"_id": user_id}, {"$set": {"locked_until": until}})

    def reset_failed_logins(self, user_id: int) -> None:
        self.collection.update_one(
            {"_id": user_id},
            {"$set": {"failed_login_attempts": 0, "locked_until": None}},
        )


def _as_utc(value):
    """MongoDB gives back dates without a timezone. They're stored in UTC, so mark them that way."""
    from datetime import timezone
    if value is not None and value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value
