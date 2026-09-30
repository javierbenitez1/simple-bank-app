from fastapi import APIRouter, status

from app.dependencies import user_service
from app.models.schemas import CreateUserRequest, UpdateUserRequest, UserResponse

router = APIRouter(prefix="/api/users", tags=["Users (Customers)"])


def to_user_response(user) -> UserResponse:
    return UserResponse(
        user_id=user.user_id,
        name=user.name,
        email=user.email,
        created_at=user.created_at,
    )


@router.get("", response_model=list[UserResponse])
def list_users():
    return [to_user_response(u) for u in user_service.list_users()]


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(request: CreateUserRequest):
    return to_user_response(user_service.create_user(request.name, request.email))


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int):
    return to_user_response(user_service.get_user(user_id))


@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, request: UpdateUserRequest):
    return to_user_response(user_service.update_user(user_id, request.name, request.email))


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int):
    user_service.delete_user(user_id)


# ----- One customer has many accounts -----

from app.controllers.account_controller import to_account_response  # noqa: E402
from app.dependencies import account_service  # noqa: E402
from app.models.schemas import AccountResponse  # noqa: E402


@router.get("/{user_id}/accounts", response_model=list[AccountResponse])
def list_user_accounts(user_id: int):
    return [to_account_response(a) for a in account_service.list_accounts_for_user(user_id)]
