from decimal import Decimal

from app.models.entities import Account, Transaction
from app.repositories.account_repository import AccountRepository
from app.repositories.transaction_repository import TransactionRepository
from app.repositories.user_repository import UserRepository
from app.services.audit_service import AuditService
from app.services.exceptions import BusinessRuleError, ConflictError, NotFoundError

# Errors that mean a money movement was attempted but rejected
AUDITED_ERRORS = (BusinessRuleError, NotFoundError)


class AccountService:
    def __init__(
        self,
        account_repo: AccountRepository,
        user_repo: UserRepository,
        txn_repo: TransactionRepository,
        audit_service: AuditService,
    ):
        self.account_repo = account_repo
        self.user_repo = user_repo
        self.txn_repo = txn_repo
        self.audit = audit_service

    # ----- Account CRUD -----

    def create_account(self, user_id: int, account_type: str) -> Account:
        if self.user_repo.find_by_id(user_id) is None:
            raise NotFoundError(f"User {user_id} not found")
        return self.account_repo.save(user_id, account_type)

    def list_accounts(self) -> list[Account]:
        return self.account_repo.find_all()

    def list_accounts_for_user(self, user_id: int) -> list[Account]:
        if self.user_repo.find_by_id(user_id) is None:
            raise NotFoundError(f"User {user_id} not found")
        return self.account_repo.find_by_user_id(user_id)

    def get_premium_accounts(self, threshold: Decimal) -> list[Account]:
        if threshold < 0:
            raise BusinessRuleError("Threshold cannot be negative")
        return self.account_repo.find_by_min_balance(threshold)

    def get_account(self, account_id: int) -> Account:
        account = self.account_repo.find_by_id(account_id)
        if account is None:
            raise NotFoundError(f"Account {account_id} not found")
        return account

    def update_account(self, account_id: int, account_type: str) -> Account:
        account = self.get_account(account_id)
        account.account_type = account_type
        return self.account_repo.update(account)

    def delete_account(self, account_id: int) -> None:
        account = self.get_account(account_id)
        if account.balance != 0:
            raise ConflictError(
                f"Account {account_id} still has a balance of {account.balance}. "
                "Withdraw or transfer the money before closing it."
            )
        self.account_repo.delete(account_id)

    # ----- Money movement (audited) -----

    def deposit(self, account_id: int, amount: Decimal) -> Account:
        try:
            if amount <= 0:
                raise BusinessRuleError("Deposit amount must be positive")
            account = self.get_account(account_id)
            account.balance += amount
            self.account_repo.update(account)
            txn = self.txn_repo.save(account_id, "DEPOSIT", amount)
        except AUDITED_ERRORS as e:
            self.audit.record("DEPOSIT", "FAILED", amount, account_id,
                              to_account_id=account_id, reason=str(e))
            raise
        self.audit.record("DEPOSIT", "SUCCESS", amount, account_id,
                          to_account_id=account_id, transaction_ids=[txn.txn_id])
        return account

    def withdraw(self, account_id: int, amount: Decimal) -> Account:
        try:
            if amount <= 0:
                raise BusinessRuleError("Withdrawal amount must be positive")
            account = self.get_account(account_id)
            if amount > account.balance:
                raise BusinessRuleError(
                    f"Insufficient funds: balance is {account.balance}, tried to withdraw {amount}"
                )
            account.balance -= amount
            self.account_repo.update(account)
            txn = self.txn_repo.save(account_id, "WITHDRAW", amount)
        except AUDITED_ERRORS as e:
            self.audit.record("WITHDRAW", "FAILED", amount, account_id,
                              from_account_id=account_id, reason=str(e))
            raise
        self.audit.record("WITHDRAW", "SUCCESS", amount, account_id,
                          from_account_id=account_id, transaction_ids=[txn.txn_id])
        return account

    def transfer(self, from_account_id: int, to_account_id: int, amount: Decimal) -> tuple[Account, Account]:
        try:
            if amount <= 0:
                raise BusinessRuleError("Transfer amount must be positive")
            if from_account_id == to_account_id:
                raise BusinessRuleError("Cannot transfer money to the same account")
            source = self.get_account(from_account_id)
            target = self.get_account(to_account_id)
            if amount > source.balance:
                raise BusinessRuleError(
                    f"Insufficient funds: balance is {source.balance}, tried to transfer {amount}"
                )
            source.balance -= amount
            target.balance += amount
            self.account_repo.update(source)
            self.account_repo.update(target)
            out_txn = self.txn_repo.save(from_account_id, "TRANSFER_OUT", amount)
            in_txn = self.txn_repo.save(to_account_id, "TRANSFER_IN", amount)
        except AUDITED_ERRORS as e:
            self.audit.record("TRANSFER", "FAILED", amount, from_account_id,
                              from_account_id=from_account_id, to_account_id=to_account_id,
                              reason=str(e))
            raise
        self.audit.record("TRANSFER", "SUCCESS", amount, from_account_id,
                          from_account_id=from_account_id, to_account_id=to_account_id,
                          transaction_ids=[out_txn.txn_id, in_txn.txn_id])
        return source, target

    def get_transactions(self, account_id: int) -> list[Transaction]:
        self.get_account(account_id)
        return self.txn_repo.find_by_account_id(account_id)
