import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.dependencies import user_service
from app.models.entities import Account, User
from app.security import decode_access_token
from app.services.exceptions import ForbiddenError, NotFoundError, UnauthorizedError

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme)) -> User:
    """Reads the token from the Authorization header and returns the logged-in user."""
    if credentials is None:
        raise UnauthorizedError("Missing token. Log in and send it as: Authorization: Bearer <token>")
    try:
        payload = decode_access_token(credentials.credentials)
        user_id = int(payload["sub"])
    except jwt.ExpiredSignatureError:
        raise UnauthorizedError("Your session expired. Please log in again.")
    except (jwt.InvalidTokenError, KeyError, ValueError):
        raise UnauthorizedError("Invalid token")
    try:
        return user_service.get_user(user_id)
    except NotFoundError:
        raise UnauthorizedError("The user for this token no longer exists")


def is_admin(user: User) -> bool:
    return user.role == "ADMIN"


def require_admin(current: User = Depends(get_current_user)) -> User:
    if not is_admin(current):
        raise ForbiddenError("Admin access required")
    return current


def ensure_self_or_admin(current: User, user_id: int) -> None:
    if current.user_id != user_id and not is_admin(current):
        raise ForbiddenError("You can only access your own customer profile")


def ensure_owns_account(current: User, account: Account) -> None:
    if account.user_id != current.user_id and not is_admin(current):
        raise ForbiddenError("You can only access your own accounts")
