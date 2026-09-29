from decimal import Decimal

from app.database import get_connection
from app.models.entities import Transaction


def _to_transaction(row) -> Transaction:
    return Transaction(
        txn_id=row["txn_id"],
        account_id=row["account_id"],
        txn_type=row["txn_type"],
        amount=row["amount"],
        created_at=row["created_at"],
    )


class TransactionRepository:
    def save(self, account_id: int, txn_type: str, amount: Decimal) -> Transaction:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO transactions (account_id, txn_type, amount) VALUES (%s, %s, %s)",
                    (account_id, txn_type, amount),
                )
                cur.execute("SELECT * FROM transactions WHERE txn_id = %s", (cur.lastrowid,))
                return _to_transaction(cur.fetchone())

    def find_by_account_id(self, account_id: int) -> list[Transaction]:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM transactions WHERE account_id = %s ORDER BY txn_id",
                    (account_id,),
                )
                return [_to_transaction(row) for row in cur.fetchall()]

    def clear(self):
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM transactions")
                cur.execute("ALTER TABLE transactions AUTO_INCREMENT = 1")