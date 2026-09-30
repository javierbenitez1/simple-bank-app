from decimal import Decimal

from fastapi import APIRouter, Query, status

from app.dependencies import account_service, user_service
from app.models.schemas import (
    AccountResponse,
    AmountRequest,
    CreateAccountRequest,
    TransactionResponse,
    TransferRequest,
    TransferResponse,
    UpdateAccountRequest,
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


@router.get("", response_model=list[AccountResponse])
def list_accounts():
    return [to_account_response(a) for a in account_service.list_accounts()]


@router.post("", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
def create_account(request: CreateAccountRequest):
    account = account_service.create_account(request.user_id, request.account_type.value)
    return to_account_response(account)


# Must be defined before /{account_id} so "premium" isn't treated as an ID
@router.get("/premium", response_model=list[AccountResponse])
def get_premium_accounts(threshold: Decimal = Query(..., description="Minimum balance to count as premium")):
    return [to_account_response(a) for a in account_service.get_premium_accounts(threshold)]


@router.post("/transfer", response_model=TransferResponse)
def transfer(request: TransferRequest):
    source, target = account_service.transfer(
        request.from_account_id, request.to_account_id, request.amount
    )
    return TransferResponse(
        from_account=to_account_response(source),
        to_account=to_account_response(target),
        amount=float(request.amount),
    )


@router.get("/{account_id}", response_model=AccountResponse)
def get_account(account_id: int):
    return to_account_response(account_service.get_account(account_id))


@router.put("/{account_id}", response_model=AccountResponse)
def update_account(account_id: int, request: UpdateAccountRequest):
    account = account_service.update_account(account_id, request.account_type.value)
    return to_account_response(account)


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(account_id: int):
    account_service.delete_account(account_id)


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
