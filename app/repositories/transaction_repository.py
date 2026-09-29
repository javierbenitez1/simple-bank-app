from decimal import Decimal

from app.models.entities import Transaction


class TransactionRepository:
    def __init__(self):
        self._transactions: dict[int, Transaction] = {}
        self._next_id = 1

    def save(self, account_id: int, txn_type: str, amount: Decimal) -> Transaction:
        txn = Transaction(txn_id=self._next_id, account_id=account_id, txn_type=txn_type, amount=amount)
        self._transactions[txn.txn_id] = txn
        self._next_id += 1
        return txn

    def find_by_account_id(self, account_id: int) -> list[Transaction]:
        return [t for t in self._transactions.values() if t.account_id == account_id]

    def clear(self):
        self._transactions.clear()
        self._next_id = 1