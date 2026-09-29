from decimal import Decimal

from app.models.entities import Account, Transaction
from app.repositories.account_repository import AccountRepository
from app.repositories.transaction_repository import TransactionRepository
from app.repositories.user_repository import UserRepository
from app.services.exceptions import BusinessRuleError, NotFoundError


class AccountService:
    def __init__(
        self,
        account_repo: AccountRepository,
        user_repo: UserRepository,
        txn_repo: TransactionRepository,
    ):
        self.account_repo = account_repo
        self.user_repo = user_repo
        self.txn_repo = txn_repo

    def create_account(self, user_id: int, account_type: str) -> Account:
        if self.user_repo.find_by_id(user_id) is None:
            raise NotFoundError(f"User {user_id} not found")
        return self.account_repo.save(user_id, account_type)

    def get_account(self, account_id: int) -> Account:
        account = self.account_repo.find_by_id(account_id)
        if account is None:
            raise NotFoundError(f"Account {account_id} not found")
        return account

    def deposit(self, account_id: int, amount: Decimal) -> Account:
        if amount <= 0:
            raise BusinessRuleError("Deposit amount must be positive")
        account = self.get_account(account_id)
        account.balance += amount
        self.account_repo.update(account)
        self.txn_repo.save(account_id, "DEPOSIT", amount)
        return account

    def withdraw(self, account_id: int, amount: Decimal) -> Account:
        if amount <= 0:
            raise BusinessRuleError("Withdrawal amount must be positive")
        account = self.get_account(account_id)
        if amount > account.balance:
            raise BusinessRuleError(
                f"Insufficient funds: balance is {account.balance}, tried to withdraw {amount}"
            )
        account.balance -= amount
        self.account_repo.update(account)
        self.txn_repo.save(account_id, "WITHDRAW", amount)
        return account

    def get_transactions(self, account_id: int) -> list[Transaction]:
        self.get_account(account_id)  # makes sure the account exists
        return self.txn_repo.find_by_account_id(account_id)