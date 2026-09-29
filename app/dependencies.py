from app.repositories.account_repository import AccountRepository
from app.repositories.transaction_repository import TransactionRepository
from app.repositories.user_repository import UserRepository
from app.services.account_service import AccountService
from app.services.user_service import UserService

user_repository = UserRepository()
account_repository = AccountRepository()
transaction_repository = TransactionRepository()

user_service = UserService(user_repository)
account_service = AccountService(account_repository, user_repository, transaction_repository)


def reset_data():
    """Clears all in-memory data. Used by the tests."""
    user_repository.clear()
    account_repository.clear()
    transaction_repository.clear()