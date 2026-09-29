from fastapi import APIRouter, status

from app.dependencies import account_service, user_service
from app.models.schemas import (
    AccountResponse,
    AmountRequest,
    CreateAccountRequest,
    TransactionResponse,
)

router = APIRouter(prefix="/api/accounts", tags=["Accounts"])


def to_account_response(account) -> AccountResponse:
    user = user_service.get_user(account.user_id)
    return AccountResponse(
        account_id=account.account_id,
        user_name=user.name,
        account_type=account.account_type,
        balance=float(account.balance),
    )


@router.post("", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
def create_account(request: CreateAccountRequest):
    account = account_service.create_account(request.user_id, request.account_type.value)
    return to_account_response(account)


@router.get("/{account_id}", response_model=AccountResponse)
def get_account(account_id: int):
    return to_account_response(account_service.get_account(account_id))


@router.post("/{account_id}/deposit", response_model=AccountResponse)
def deposit(account_id: int, request: AmountRequest):
    return to_account_response(account_service.deposit(account_id, request.amount))


@router.post("/{account_id}/withdraw", response_model=AccountResponse)
def withdraw(account_id: int, request: AmountRequest):
    return to_account_response(account_service.withdraw(account_id, request.amount))


@router.get("/{account_id}/transactions", response_model=list[TransactionResponse])
def get_transactions(account_id: int):
    return [
        TransactionResponse(
            transaction_id=t.txn_id,
            type=t.txn_type,
            amount=float(t.amount),
            date=t.created_at,
        )
        for t in account_service.get_transactions(account_id)
    ]