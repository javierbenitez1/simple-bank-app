from typing import Optional

from app.database import get_connection
from app.models.entities import User


def _to_user(row) -> User:
    return User(
        user_id=row["user_id"],
        name=row["name"],
        email=row["email"],
        created_at=row["created_at"],
    )


class UserRepository:
    def save(self, name: str, email: str) -> User:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO users (name, email) VALUES (%s, %s)", (name, email))
                cur.execute("SELECT * FROM users WHERE user_id = %s", (cur.lastrowid,))
                return _to_user(cur.fetchone())

    def find_by_id(self, user_id: int) -> Optional[User]:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
                row = cur.fetchone()
                return _to_user(row) if row else None

    def find_by_email(self, email: str) -> Optional[User]:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM users WHERE email = %s", (email,))
                row = cur.fetchone()
                return _to_user(row) if row else None

    def clear(self):
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM users")
                cur.execute("ALTER TABLE users AUTO_INCREMENT = 1")