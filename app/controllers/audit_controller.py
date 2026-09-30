from fastapi import APIRouter, Depends, Query

from app.auth_dependencies import require_admin

from app.dependencies import audit_service
from app.models.schemas import AuditLogResponse

router = APIRouter(prefix="/api/audit", tags=["Audit"], dependencies=[Depends(require_admin)])


def to_audit_response(log) -> AuditLogResponse:
    return AuditLogResponse(
        audit_id=log.audit_id,
        action=log.action,
        status=log.status,
        amount=float(log.amount),
        performed_by_user_id=log.performed_by_user_id,
        performed_by_name=log.performed_by_name,
        from_account_id=log.from_account_id,
        to_account_id=log.to_account_id,
        transaction_ids=log.transaction_ids,
        reason=log.reason,
        timestamp=log.timestamp,
    )


@router.get("", response_model=list[AuditLogResponse])
def list_audit_logs(
    account_id: int | None = Query(None, alias="accountId"),
    user_id: int | None = Query(None, alias="userId"),
    action: str | None = Query(None, description="DEPOSIT, WITHDRAW, or TRANSFER"),
    result: str | None = Query(None, alias="status", description="SUCCESS or FAILED"),
):
    logs = audit_service.list_logs(account_id, user_id, action, result)
    return [to_audit_response(log) for log in logs]


@router.get("/transaction/{transaction_id}", response_model=AuditLogResponse)
def trace_transaction(transaction_id: int):
    return to_audit_response(audit_service.trace_transaction(transaction_id))


@router.get("/{audit_id}", response_model=AuditLogResponse)
def get_audit_log(audit_id: int):
    return to_audit_response(audit_service.get_log(audit_id))
