from fastapi import APIRouter, status

from app.dependencies import user_service
from app.models.schemas import CreateUserRequest, UserResponse

router = APIRouter(prefix="/api/users", tags=["Users"])


def to_user_response(user) -> UserResponse:
    return UserResponse(
        user_id=user.user_id,
        name=user.name,
        email=user.email,
        created_at=user.created_at,
    )


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(request: CreateUserRequest):
    user = user_service.create_user(request.name, request.email)
    return to_user_response(user)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int):
    return to_user_response(user_service.get_user(user_id))