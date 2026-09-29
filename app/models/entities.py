from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal


def now():
    return datetime.now(timezone.utc)


@dataclass
class User:
    user_id: int
    name: str
    email: str
    created_at: datetime = field(default_factory=now)


@dataclass
class Account:
    account_id: int
    user_id: int
    account_type: str
    balance: Decimal = Decimal("0.00")
    created_at: datetime = field(default_factory=now)


@dataclass
class Transaction:
    txn_id: int
    account_id: int
    txn_type: str
    amount: Decimal
    created_at: datetime = field(default_factory=now)