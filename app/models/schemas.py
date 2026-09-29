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