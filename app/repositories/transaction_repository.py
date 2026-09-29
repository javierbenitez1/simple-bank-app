from decimal import Decimal

from bson.decimal128 import Decimal128

from app.database import get_db, next_id, reset_counter
from app.models.entities import Transaction


def _to_transaction(doc) -> Transaction:
    return Transaction(
        txn_id=doc["_id"],
        account_id=doc["account_id"],
        txn_type=doc["txn_type"],
        amount=doc["amount"].to_decimal(),
        created_at=doc["created_at"],
    )


class TransactionRepository:
    @property
    def collection(self):
        return get_db().transactions

    def save(self, account_id: int, txn_type: str, amount: Decimal) -> Transaction:
        txn = Transaction(txn_id=next_id("transactions"), account_id=account_id, txn_type=txn_type, amount=amount)
        self.collection.insert_one({
            "_id": txn.txn_id,
            "account_id": txn.account_id,
            "txn_type": txn.txn_type,
            "amount": Decimal128(str(txn.amount)),
            "created_at": txn.created_at,
        })
        return txn

    def find_by_account_id(self, account_id: int) -> list[Transaction]:
        docs = self.collection.find({"account_id": account_id}).sort("_id", 1)
        return [_to_transaction(doc) for doc in docs]

    def clear(self):
        self.collection.delete_many({})
        reset_counter("transactions")
