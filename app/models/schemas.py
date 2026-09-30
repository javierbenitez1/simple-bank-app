from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class CamelModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class AccountType(str, Enum):
    SAVINGS = "SAVINGS"
    CHECKING = "CHECKING"


class TransactionType(str, Enum):
    DEPOSIT = "DEPOSIT"
    WITHDRAW = "WITHDRAW"
    TRANSFER_OUT = "TRANSFER_OUT"
    TRANSFER_IN = "TRANSFER_IN"


# ----- Requests -----

class CreateUserRequest(CamelModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., max_length=100, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class CreateAccountRequest(CamelModel):
    user_id: int
    account_type: AccountType


class AmountRequest(CamelModel):
    amount: Decimal = Field(..., max_digits=10, decimal_places=2)


# ----- Responses -----

class UserResponse(CamelModel):
    user_id: int
    name: str
    email: str
    created_at: datetime


class AccountResponse(CamelModel):
    account_id: int
    user_name: str
    account_type: AccountType
    balance: float


class TransactionResponse(CamelModel):
    transaction_id: int
    type: TransactionType
    amount: float
    date: datetime

class UpdateUserRequest(CamelModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    email: str | None = Field(None, max_length=100, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class UpdateAccountRequest(CamelModel):
    account_type: AccountType


class TransferRequest(CamelModel):
    from_account_id: int
    to_account_id: int
    amount: Decimal = Field(..., max_digits=10, decimal_places=2)


class TransferResponse(CamelModel):
    from_account: AccountResponse
    to_account: AccountResponse
    amount: float


class AuditLogResponse(CamelModel):
    audit_id: int
    action: str
    status: str
    amount: float
    performed_by_user_id: int | None
    performed_by_name: str | None
    from_account_id: int | None
    to_account_id: int | None
    transaction_ids: list[int]
    reason: str | None
    timestamp: datetime
