from fastapi import APIRouter, Depends

from app.auth_dependencies import ensure_self_or_admin, get_current_user, require_admin
from app.controllers.account_controller import to_account_response
from app.controllers.audit_controller import to_audit_response
from app.controllers.user_controller import to_user_response
from app.dependencies import dashboard_service
from app.models.entities import User
from app.models.schemas import (
    AdminDashboardResponse,
    CustomerDashboardResponse,
    DashboardTransactionResponse,
)

router = APIRouter(prefix="/api", tags=["Dashboards"])


@router.get("/admin", response_model=AdminDashboardResponse)
def admin_dashboard(current: User = Depends(require_admin)):
    """Admin token: allowed. Customer token: 403 Forbidden. No token: 401."""
    s = dashboard_service.admin_summary()
    return AdminDashboardResponse(
        admin_name=current.name,
        total_customers=s["total_customers"],
        total_accounts=s["total_accounts"],
        total_deposits=float(s["total_deposits"]),
        failed_attempts=s["failed_attempts"],
        recent_activity=[to_audit_response(log) for log in s["recent_activity"]],
    )


@router.get("/customerDashboard/{user_id}", response_model=CustomerDashboardResponse)
def customer_dashboard(user_id: int, current: User = Depends(get_current_user)):
    """Customers can only open their own dashboard. Admins can open anyone's."""
    ensure_self_or_admin(current, user_id)
    s = dashboard_service.customer_summary(user_id)
    return CustomerDashboardResponse(
        customer=to_user_response(s["user"]),
        total_balance=float(s["total_balance"]),
        accounts=[to_account_response(a) for a in s["accounts"]],
        recent_transactions=[
            DashboardTransactionResponse(
                transaction_id=t.txn_id,
                account_id=t.account_id,
                type=t.txn_type,
                amount=float(t.amount),
                date=t.created_at,
            )
            for t in s["recent_transactions"]
        ],
    )
