from fastapi import APIRouter, Depends

from app.auth_dependencies import get_current_user
from app.controllers.user_controller import to_user_response
from app.dependencies import user_service
from app.models.entities import User
from app.models.schemas import LoginRequest, TokenResponse, UserResponse
from app.security import EXPIRE_MINUTES, create_access_token

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest):
    user = user_service.authenticate(request.email, request.password)
    return TokenResponse(
        access_token=create_access_token(user.user_id, user.role),
        expires_in=EXPIRE_MINUTES * 60,
        user=to_user_response(user),
    )


@router.get("/me", response_model=UserResponse)
def me(current: User = Depends(get_current_user)):
    return to_user_response(current)
