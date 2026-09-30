from typing import Optional

from bson.decimal128 import Decimal128

from app.database import get_db, next_id, reset_counter
from app.models.entities import AuditLog


def _to_log(doc) -> AuditLog:
    return AuditLog(
        audit_id=doc["_id"],
        action=doc["action"],
        status=doc["status"],
        amount=doc["amount"].to_decimal(),
        performed_by_user_id=doc.get("performed_by_user_id"),
        performed_by_name=doc.get("performed_by_name"),
        from_account_id=doc.get("from_account_id"),
        to_account_id=doc.get("to_account_id"),
        transaction_ids=doc.get("transaction_ids", []),
        reason=doc.get("reason"),
        timestamp=doc["timestamp"],
    )


class AuditRepository:
    @property
    def collection(self):
        return get_db().audit_logs

    def save(self, log: AuditLog) -> AuditLog:
        log.audit_id = next_id("audit_logs")
        self.collection.insert_one({
            "_id": log.audit_id,
            "action": log.action,
            "status": log.status,
            "amount": Decimal128(str(log.amount)),
            "performed_by_user_id": log.performed_by_user_id,
            "performed_by_name": log.performed_by_name,
            "from_account_id": log.from_account_id,
            "to_account_id": log.to_account_id,
            "transaction_ids": log.transaction_ids,
            "reason": log.reason,
            "timestamp": log.timestamp,
        })
        return log

    def find(
        self,
        account_id: int | None = None,
        user_id: int | None = None,
        action: str | None = None,
        status: str | None = None,
    ) -> list[AuditLog]:
        query = {}
        if account_id is not None:
            query["$or"] = [{"from_account_id": account_id}, {"to_account_id": account_id}]
        if user_id is not None:
            query["performed_by_user_id"] = user_id
        if action:
            query["action"] = action.upper()
        if status:
            query["status"] = status.upper()
        return [_to_log(doc) for doc in self.collection.find(query).sort("_id", -1)]

    def find_by_id(self, audit_id: int) -> Optional[AuditLog]:
        doc = self.collection.find_one({"_id": audit_id})
        return _to_log(doc) if doc else None

    def find_by_transaction_id(self, transaction_id: int) -> Optional[AuditLog]:
        doc = self.collection.find_one({"transaction_ids": transaction_id})
        return _to_log(doc) if doc else None

    def clear(self):
        self.collection.delete_many({})
        reset_counter("audit_logs")
