from typing import Optional

from app.database import get_connection
from app.models.entities import Account


def _to_account(row) -> Account:
    return Account(
        account_id=row["account_id"],
        user_id=row["user_id"],
        account_type=row["account_type"],
        balance=row["balance"],
        created_at=row["created_at"],
    )


class AccountRepository:
    def save(self, user_id: int, account_type: str) -> Account:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO accounts (user_id, account_type) VALUES (%s, %s)",
                    (user_id, account_type),
                )
                cur.execute("SELECT * FROM accounts WHERE account_id = %s", (cur.lastrowid,))
                return _to_account(cur.fetchone())

    def find_by_id(self, account_id: int) -> Optional[Account]:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM accounts WHERE account_id = %s", (account_id,))
                row = cur.fetchone()
                return _to_account(row) if row else None

    def update(self, account: Account) -> Account:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE accounts SET balance = %s, account_type = %s WHERE account_id = %s",
                    (account.balance, account.account_type, account.account_id),
                )
        return account

    def clear(self):
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM accounts")
                cur.execute("ALTER TABLE accounts AUTO_INCREMENT = 1")