from decimal import Decimal

from fastapi import APIRouter, Depends, Query, status

from app.auth_dependencies import ensure_owns_account, ensure_self_or_admin, get_current_user, require_admin
from app.dependencies import account_service, user_service
from app.models.entities import User
from app.models.schemas import (
    AccountResponse,
    AmountRequest,
    CreateAccountRequest,
    TransactionResponse,
    TransferRequest,
    TransferResponse,
    UpdateAccountRequest,
)
from app.services.exceptions import NotFoundError

router = APIRouter(prefix="/api/accounts", tags=["Accounts"])


def to_account_response(account) -> AccountResponse:
    user = user_service.get_user(account.user_id)
    return AccountResponse(
        account_id=account.account_id,
        user_name=user.name,
        account_type=account.account_type,
        balance=float(account.balance),
    )


def authorize_account(current: User, account_id: int) -> None:
    """Blocks access to other people's accounts. If the account doesn't exist,
    we let the service raise the 404 so failed money movements still get audited."""
    try:
        account = account_service.get_account(account_id)
    except NotFoundError:
        return
    ensure_owns_account(current, account)


@router.get("", response_model=list[AccountResponse])
def list_accounts(_: User = Depends(require_admin)):
    return [to_account_response(a) for a in account_service.list_accounts()]


@router.post("", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
def create_account(request: CreateAccountRequest, current: User = Depends(get_current_user)):
    ensure_self_or_admin(current, request.user_id)
    account = account_service.create_account(request.user_id, request.account_type.value)
    return to_account_response(account)


# Must be defined before /{account_id} so "premium" isn't treated as an ID
@router.get("/premium", response_model=list[AccountResponse])
def get_premium_accounts(
    threshold: Decimal = Query(..., description="Minimum balance to count as premium"),
    _: User = Depends(require_admin),
):
    return [to_account_response(a) for a in account_service.get_premium_accounts(threshold)]


@router.post("/transfer", response_model=TransferResponse)
def transfer(request: TransferRequest, current: User = Depends(get_current_user)):
    # You can only send money FROM your own account, but you can send it TO anyone
    authorize_account(current, request.from_account_id)
    source, target = account_service.transfer(
        request.from_account_id, request.to_account_id, request.amount, actor_id=current.user_id
    )
    return TransferResponse(
        from_account=to_account_response(source),
        to_account=to_account_response(target),
        amount=float(request.amount),
    )


@router.get("/{account_id}", response_model=AccountResponse)
def get_account(account_id: int, current: User = Depends(get_current_user)):
    account = account_service.get_account(account_id)
    ensure_owns_account(current, account)
    return to_account_response(account)


@router.put("/{account_id}", response_model=AccountResponse)
def update_account(account_id: int, request: UpdateAccountRequest, current: User = Depends(get_current_user)):
    authorize_account(current, account_id)
    account = account_service.update_account(account_id, request.account_type.value)
    return to_account_response(account)


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(account_id: int, current: User = Depends(get_current_user)):
    authorize_account(current, account_id)
    account_service.delete_account(account_id)


@router.post("/{account_id}/deposit", response_model=AccountResponse)
def deposit(account_id: int, request: AmountRequest, current: User = Depends(get_current_user)):
    authorize_account(current, account_id)
    account = account_service.deposit(account_id, request.amount, actor_id=current.user_id)
    return to_account_response(account)


@router.post("/{account_id}/withdraw", response_model=AccountResponse)
def withdraw(account_id: int, request: AmountRequest, current: User = Depends(get_current_user)):
    authorize_account(current, account_id)
    account = account_service.withdraw(account_id, request.amount, actor_id=current.user_id)
    return to_account_response(account)


@router.get("/{account_id}/transactions", response_model=list[TransactionResponse])
def get_transactions(account_id: int, current: User = Depends(get_current_user)):
    authorize_account(current, account_id)
    return [
        TransactionResponse(
            transaction_id=t.txn_id,
            type=t.txn_type,
            amount=float(t.amount),
            date=t.created_at,
        )
        for t in account_service.get_transactions(account_id)
    ]
