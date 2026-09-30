from app.repositories.account_repository import AccountRepository
from app.repositories.audit_repository import AuditRepository
from app.repositories.transaction_repository import TransactionRepository
from app.repositories.user_repository import UserRepository
from app.services.account_service import AccountService
from app.services.audit_service import AuditService
from app.services.user_service import UserService

user_repository = UserRepository()
account_repository = AccountRepository()
transaction_repository = TransactionRepository()
audit_repository = AuditRepository()

audit_service = AuditService(audit_repository, account_repository, user_repository)
user_service = UserService(user_repository, account_repository)
account_service = AccountService(
    account_repository, user_repository, transaction_repository, audit_service
)


def reset_data():
    """Clears all data. Used by the tests."""
    audit_repository.clear()
    transaction_repository.clear()
    account_repository.clear()
    user_repository.clear()
