from decimal import Decimal

from app.models.entities import AuditLog
from app.repositories.account_repository import AccountRepository
from app.repositories.audit_repository import AuditRepository
from app.repositories.user_repository import UserRepository
from app.services.exceptions import NotFoundError


class AuditService:
    def __init__(
        self,
        audit_repo: AuditRepository,
        account_repo: AccountRepository,
        user_repo: UserRepository,
    ):
        self.audit_repo = audit_repo
        self.account_repo = account_repo
        self.user_repo = user_repo

    def record(
        self,
        action: str,
        status: str,
        amount: Decimal,
        initiator_account_id: int,
        from_account_id: int | None = None,
        to_account_id: int | None = None,
        transaction_ids: list[int] | None = None,
        reason: str | None = None,
    ) -> AuditLog:
        """Records who did what, when, to which accounts, and whether it worked."""
        user_id, user_name = None, None
        account = self.account_repo.find_by_id(initiator_account_id)
        if account:
            user = self.user_repo.find_by_id(account.user_id)
            user_id = account.user_id
            user_name = user.name if user else None

        return self.audit_repo.save(AuditLog(
            action=action,
            status=status,
            amount=amount,
            performed_by_user_id=user_id,
            performed_by_name=user_name,
            from_account_id=from_account_id,
            to_account_id=to_account_id,
            transaction_ids=transaction_ids or [],
            reason=reason,
        ))

    def list_logs(self, account_id=None, user_id=None, action=None, status=None) -> list[AuditLog]:
        return self.audit_repo.find(account_id, user_id, action, status)

    def get_log(self, audit_id: int) -> AuditLog:
        log = self.audit_repo.find_by_id(audit_id)
        if log is None:
            raise NotFoundError(f"Audit log {audit_id} not found")
        return log

    def trace_transaction(self, transaction_id: int) -> AuditLog:
        log = self.audit_repo.find_by_transaction_id(transaction_id)
        if log is None:
            raise NotFoundError(f"No audit record found for transaction {transaction_id}")
        return log
