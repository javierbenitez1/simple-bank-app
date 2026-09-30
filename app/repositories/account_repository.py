from decimal import Decimal
from typing import Optional

from bson.decimal128 import Decimal128

from app.database import get_db, next_id, reset_counter
from app.models.entities import Account


def _to_account(doc) -> Account:
    return Account(
        account_id=doc["_id"],
        user_id=doc["user_id"],
        account_type=doc["account_type"],
        balance=doc["balance"].to_decimal(),
        created_at=doc["created_at"],
    )


class AccountRepository:
    @property
    def collection(self):
        return get_db().accounts

    def save(self, user_id: int, account_type: str) -> Account:
        account = Account(account_id=next_id("accounts"), user_id=user_id, account_type=account_type)
        self.collection.insert_one({
            "_id": account.account_id,
            "user_id": account.user_id,
            "account_type": account.account_type,
            "balance": Decimal128(str(account.balance)),
            "created_at": account.created_at,
        })
        return account

    def find_all(self) -> list[Account]:
        return [_to_account(doc) for doc in self.collection.find().sort("_id", 1)]

    def find_by_id(self, account_id: int) -> Optional[Account]:
        doc = self.collection.find_one({"_id": account_id})
        return _to_account(doc) if doc else None

    def find_by_user_id(self, user_id: int) -> list[Account]:
        docs = self.collection.find({"user_id": user_id}).sort("_id", 1)
        return [_to_account(doc) for doc in docs]

    def find_by_min_balance(self, threshold: Decimal) -> list[Account]:
        docs = self.collection.find({"balance": {"$gte": Decimal128(str(threshold))}}).sort("_id", 1)
        return [_to_account(doc) for doc in docs]

    def update(self, account: Account) -> Account:
        self.collection.update_one(
            {"_id": account.account_id},
            {"$set": {
                "balance": Decimal128(str(account.balance)),
                "account_type": account.account_type,
            }},
        )
        return account

    def delete(self, account_id: int) -> bool:
        return self.collection.delete_one({"_id": account_id}).deleted_count == 1

    def clear(self):
        self.collection.delete_many({})
        reset_counter("accounts")
