from typing import Optional

from app.models.entities import Account


class AccountRepository:
    def __init__(self):
        self._accounts: dict[int, Account] = {}
        self._next_id = 1

    def save(self, user_id: int, account_type: str) -> Account:
        account = Account(account_id=self._next_id, user_id=user_id, account_type=account_type)
        self._accounts[account.account_id] = account
        self._next_id += 1
        return account

    def find_by_id(self, account_id: int) -> Optional[Account]:
        return self._accounts.get(account_id)

    def update(self, account: Account) -> Account:
        self._accounts[account.account_id] = account
        return account

    def clear(self):
        self._accounts.clear()
        self._next_id = 1