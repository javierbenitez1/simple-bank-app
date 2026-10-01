from fastapi import APIRouter, Depends, status

from app.auth_dependencies import ensure_self_or_admin, get_current_user, require_admin
from app.controllers.account_controller import to_account_response
from app.dependencies import account_service, user_service
from app.models.entities import User
from app.models.schemas import AccountResponse, RegisterRequest, UpdateUserRequest, UserResponse

router = APIRouter(prefix="/api/users", tags=["Users (Customers)"])


def to_user_response(user) -> UserResponse:
    return UserResponse(
        user_id=user.user_id,
        role=user.role,
        username=user.username,
        name=user.name,
        email=user.email,
        created_at=user.created_at,
    )


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(request: RegisterRequest):
    """Public: anyone can sign up as a customer."""
    return to_user_response(user_service.create_user(request.name, request.email, request.password, username=request.username))


@router.get("", response_model=list[UserResponse])
def list_users(_: User = Depends(require_admin)):
    return [to_user_response(u) for u in user_service.list_users()]


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, current: User = Depends(get_current_user)):
    ensure_self_or_admin(current, user_id)
    return to_user_response(user_service.get_user(user_id))


@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, request: UpdateUserRequest, current: User = Depends(get_current_user)):
    ensure_self_or_admin(current, user_id)
    return to_user_response(user_service.update_user(user_id, request.name, request.email))


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, current: User = Depends(get_current_user)):
    ensure_self_or_admin(current, user_id)
    user_service.delete_user(user_id)


@router.get("/{user_id}/accounts", response_model=list[AccountResponse])
def list_user_accounts(user_id: int, current: User = Depends(get_current_user)):
    ensure_self_or_admin(current, user_id)
    return [to_account_response(a) for a in account_service.list_accounts_for_user(user_id)]
