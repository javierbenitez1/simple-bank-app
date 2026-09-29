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

    def find_by_id(self, account_id: int) -> Optional[Account]:
        doc = self.collection.find_one({"_id": account_id})
        return _to_account(doc) if doc else None

    def update(self, account: Account) -> Account:
        self.collection.update_one(
            {"_id": account.account_id},
            {"$set": {
                "balance": Decimal128(str(account.balance)),
                "account_type": account.account_type,
            }},
        )
        return account

    def clear(self):
        self.collection.delete_many({})
        reset_counter("accounts")
