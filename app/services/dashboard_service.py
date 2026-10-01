from decimal import Decimal

from app.repositories.account_repository import AccountRepository
from app.repositories.audit_repository import AuditRepository
from app.repositories.transaction_repository import TransactionRepository
from app.repositories.user_repository import UserRepository
from app.services.exceptions import NotFoundError


class DashboardService:
    def __init__(
        self,
        user_repo: UserRepository,
        account_repo: AccountRepository,
        txn_repo: TransactionRepository,
        audit_repo: AuditRepository,
    ):
        self.user_repo = user_repo
        self.account_repo = account_repo
        self.txn_repo = txn_repo
        self.audit_repo = audit_repo

    def admin_summary(self) -> dict:
        """Bank-wide numbers for the admin dashboard."""
        users = self.user_repo.find_all()
        accounts = self.account_repo.find_all()
        return {
            "total_customers": sum(1 for u in users if u.role == "CUSTOMER"),
            "total_accounts": len(accounts),
            "total_deposits": sum((a.balance for a in accounts), Decimal("0")),
            "failed_attempts": len(self.audit_repo.find(status="FAILED")),
            "recent_activity": self.audit_repo.find()[:5],
        }

    def customer_summary(self, user_id: int) -> dict:
        """One customer's profile, accounts, total balance, and latest transactions."""
        user = self.user_repo.find_by_id(user_id)
        if user is None:
            raise NotFoundError(f"User {user_id} not found")
        accounts = self.account_repo.find_by_user_id(user_id)
        transactions = [t for a in accounts for t in self.txn_repo.find_by_account_id(a.account_id)]
        transactions.sort(key=lambda t: t.txn_id, reverse=True)
        return {
            "user": user,
            "accounts": accounts,
            "total_balance": sum((a.balance for a in accounts), Decimal("0")),
            "recent_transactions": transactions[:5],
        }
