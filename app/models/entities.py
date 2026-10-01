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
    password_hash: str | None = None
    role: str = "CUSTOMER"
    username: str | None = None


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

@dataclass
class AuditLog:
    action: str                       # DEPOSIT, WITHDRAW, TRANSFER
    status: str                       # SUCCESS or FAILED
    amount: Decimal
    audit_id: int | None = None
    performed_by_user_id: int | None = None
    performed_by_name: str | None = None
    from_account_id: int | None = None
    to_account_id: int | None = None
    transaction_ids: list[int] = field(default_factory=list)
    reason: str | None = None         # why it failed, if it failed
    timestamp: datetime = field(default_factory=now)
