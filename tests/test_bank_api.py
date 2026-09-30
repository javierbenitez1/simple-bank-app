import os
os.environ["MONGODB_DB_NAME"] = "simple_bank_test"

import pytest
from fastapi.testclient import TestClient

from app.dependencies import reset_data, user_service
from app.main import app

client = TestClient(app)
PASSWORD = "password123"


@pytest.fixture(autouse=True)
def clean_data():
    reset_data()


# ----- Helpers -----

def register(name="Test User", email="test@example.com"):
    res = client.post("/api/users", json={"name": name, "email": email, "password": PASSWORD})
    assert res.status_code == 201
    return res.json()


def login(email):
    res = client.post("/api/auth/login", json={"email": email, "password": PASSWORD})
    return {"Authorization": f"Bearer {res.json()['accessToken']}"}


def make_customer(name="Test User", email="test@example.com"):
    """Signs up a customer and returns (user_id, auth headers)."""
    user = register(name, email)
    return user["userId"], login(email)


def make_admin():
    """Admins can't sign up through the API, so create one directly."""
    admin = user_service.create_user("Admin", "admin@example.com", PASSWORD, role="ADMIN")
    return admin.user_id, login("admin@example.com")


def open_account(headers, user_id, account_type="SAVINGS", deposit=0):
    res = client.post("/api/accounts", json={"userId": user_id, "accountType": account_type}, headers=headers)
    assert res.status_code == 201
    account_id = res.json()["accountId"]
    if deposit:
        client.post(f"/api/accounts/{account_id}/deposit", json={"amount": deposit}, headers=headers)
    return account_id


# ----- Health -----

def test_health_check():
    assert client.get("/").status_code == 200


# ----- Auth -----

def test_register_creates_customer():
    user = register()
    assert user["role"] == "CUSTOMER"
    assert "password" not in user and "passwordHash" not in user


def test_password_is_hashed():
    user = register()
    stored = user_service.get_user(user["userId"]).password_hash
    assert stored != PASSWORD
    assert stored.startswith("$2")  # bcrypt hashes start with $2


def test_short_password_rejected():
    res = client.post("/api/users", json={"name": "A", "email": "a@example.com", "password": "short"})
    assert res.status_code == 422


def test_duplicate_email_returns_409():
    register()
    res = client.post("/api/users", json={"name": "B", "email": "test@example.com", "password": PASSWORD})
    assert res.status_code == 409


def test_login_returns_token():
    register()
    res = client.post("/api/auth/login", json={"email": "test@example.com", "password": PASSWORD})
    assert res.status_code == 200
    body = res.json()
    assert body["tokenType"] == "bearer"
    assert body["accessToken"].count(".") == 2  # header.payload.signature
    assert body["user"]["email"] == "test@example.com"


def test_login_wrong_password_returns_401():
    register()
    res = client.post("/api/auth/login", json={"email": "test@example.com", "password": "wrong-password"})
    assert res.status_code == 401


def test_login_unknown_email_returns_401():
    res = client.post("/api/auth/login", json={"email": "nobody@example.com", "password": PASSWORD})
    assert res.status_code == 401


def test_me_returns_current_user():
    user_id, headers = make_customer()
    res = client.get("/api/auth/me", headers=headers)
    assert res.status_code == 200
    assert res.json()["userId"] == user_id


def test_missing_token_returns_401():
    assert client.get("/api/auth/me").status_code == 401


def test_invalid_token_returns_401():
    res = client.get("/api/auth/me", headers={"Authorization": "Bearer not-a-real-token"})
    assert res.status_code == 401


# ----- Customers -----

def test_customer_can_view_own_profile():
    user_id, headers = make_customer()
    assert client.get(f"/api/users/{user_id}", headers=headers).status_code == 200


def test_customer_cannot_view_other_profile():
    _, headers = make_customer()
    other_id, _ = make_customer("Other", "other@example.com")
    assert client.get(f"/api/users/{other_id}", headers=headers).status_code == 403


def test_only_admin_can_list_users():
    _, customer = make_customer()
    _, admin = make_admin()
    assert client.get("/api/users", headers=customer).status_code == 403
    assert len(client.get("/api/users", headers=admin).json()) == 2


def test_update_own_profile():
    user_id, headers = make_customer()
    res = client.put(f"/api/users/{user_id}", json={"name": "New Name"}, headers=headers)
    assert res.status_code == 200
    assert res.json()["name"] == "New Name"


def test_update_to_taken_email_returns_409():
    make_customer("A", "a@example.com")
    b_id, b_headers = make_customer("B", "b@example.com")
    res = client.put(f"/api/users/{b_id}", json={"email": "a@example.com"}, headers=b_headers)
    assert res.status_code == 409


def test_delete_own_profile():
    user_id, headers = make_customer()
    assert client.delete(f"/api/users/{user_id}", headers=headers).status_code == 204
    _, admin = make_admin()
    assert client.get(f"/api/users/{user_id}", headers=admin).status_code == 404


def test_cannot_delete_user_with_accounts():
    user_id, headers = make_customer()
    open_account(headers, user_id)
    assert client.delete(f"/api/users/{user_id}", headers=headers).status_code == 409


# ----- Accounts -----

def test_create_account_for_self():
    user_id, headers = make_customer()
    res = client.post("/api/accounts", json={"userId": user_id, "accountType": "SAVINGS"}, headers=headers)
    assert res.status_code == 201
    assert res.json()["userName"] == "Test User"
    assert res.json()["balance"] == 0


def test_cannot_create_account_for_someone_else():
    _, headers = make_customer()
    other_id, _ = make_customer("Other", "other@example.com")
    res = client.post("/api/accounts", json={"userId": other_id, "accountType": "SAVINGS"}, headers=headers)
    assert res.status_code == 403


def test_customer_has_many_accounts():
    user_id, headers = make_customer()
    open_account(headers, user_id, "SAVINGS")
    open_account(headers, user_id, "CHECKING")
    accounts = client.get(f"/api/users/{user_id}/accounts", headers=headers).json()
    assert [a["accountType"] for a in accounts] == ["SAVINGS", "CHECKING"]


def test_cannot_view_someone_elses_account():
    other_id, other = make_customer("Other", "other@example.com")
    account_id = open_account(other, other_id)
    _, headers = make_customer()
    assert client.get(f"/api/accounts/{account_id}", headers=headers).status_code == 403


def test_admin_can_view_any_account():
    user_id, headers = make_customer()
    account_id = open_account(headers, user_id)
    _, admin = make_admin()
    assert client.get(f"/api/accounts/{account_id}", headers=admin).status_code == 200


def test_only_admin_can_list_all_accounts():
    user_id, customer = make_customer()
    open_account(customer, user_id)
    _, admin = make_admin()
    assert client.get("/api/accounts", headers=customer).status_code == 403
    assert len(client.get("/api/accounts", headers=admin).json()) == 1


def test_deposit_increases_balance():
    user_id, headers = make_customer()
    account_id = open_account(headers, user_id)
    res = client.post(f"/api/accounts/{account_id}/deposit", json={"amount": 500}, headers=headers)
    assert res.status_code == 200
    assert res.json()["balance"] == 500


def test_deposit_must_be_positive():
    user_id, headers = make_customer()
    account_id = open_account(headers, user_id)
    res = client.post(f"/api/accounts/{account_id}/deposit", json={"amount": -50}, headers=headers)
    assert res.status_code == 400


def test_withdraw_decreases_balance():
    user_id, headers = make_customer()
    account_id = open_account(headers, user_id, deposit=500)
    res = client.post(f"/api/accounts/{account_id}/withdraw", json={"amount": 200}, headers=headers)
    assert res.json()["balance"] == 300


def test_cannot_withdraw_more_than_balance():
    user_id, headers = make_customer()
    account_id = open_account(headers, user_id, deposit=100)
    res = client.post(f"/api/accounts/{account_id}/withdraw", json={"amount": 500}, headers=headers)
    assert res.status_code == 400
    assert client.get(f"/api/accounts/{account_id}", headers=headers).json()["balance"] == 100


def test_cannot_deposit_into_someone_elses_account():
    other_id, other = make_customer("Other", "other@example.com")
    account_id = open_account(other, other_id)
    _, headers = make_customer()
    res = client.post(f"/api/accounts/{account_id}/deposit", json={"amount": 50}, headers=headers)
    assert res.status_code == 403


def test_transactions_are_recorded():
    user_id, headers = make_customer()
    account_id = open_account(headers, user_id, deposit=500)
    client.post(f"/api/accounts/{account_id}/withdraw", json={"amount": 200}, headers=headers)
    client.post(f"/api/accounts/{account_id}/withdraw", json={"amount": 9999}, headers=headers)  # fails
    txns = client.get(f"/api/accounts/{account_id}/transactions", headers=headers).json()
    assert [t["type"] for t in txns] == ["DEPOSIT", "WITHDRAW"]


def test_get_missing_account_returns_404():
    _, admin = make_admin()
    assert client.get("/api/accounts/999", headers=admin).status_code == 404


def test_update_account_type():
    user_id, headers = make_customer()
    account_id = open_account(headers, user_id)
    res = client.put(f"/api/accounts/{account_id}", json={"accountType": "CHECKING"}, headers=headers)
    assert res.status_code == 200
    assert res.json()["accountType"] == "CHECKING"


def test_delete_empty_account():
    user_id, headers = make_customer()
    account_id = open_account(headers, user_id)
    assert client.delete(f"/api/accounts/{account_id}", headers=headers).status_code == 204


def test_cannot_delete_account_with_balance():
    user_id, headers = make_customer()
    account_id = open_account(headers, user_id, deposit=100)
    assert client.delete(f"/api/accounts/{account_id}", headers=headers).status_code == 409


def test_premium_accounts_admin_only():
    user_id, customer = make_customer()
    open_account(customer, user_id, deposit=500)
    rich = open_account(customer, user_id, deposit=2000)
    _, admin = make_admin()
    assert client.get("/api/accounts/premium", params={"threshold": 1000}, headers=customer).status_code == 403
    premium = client.get("/api/accounts/premium", params={"threshold": 1000}, headers=admin).json()
    assert [a["accountId"] for a in premium] == [rich]


# ----- Transfers -----

def test_transfer_between_own_accounts():
    user_id, headers = make_customer()
    a = open_account(headers, user_id, deposit=500)
    b = open_account(headers, user_id, "CHECKING")
    res = client.post("/api/accounts/transfer", json={"fromAccountId": a, "toAccountId": b, "amount": 200}, headers=headers)
    assert res.status_code == 200
    assert res.json()["fromAccount"]["balance"] == 300
    assert res.json()["toAccount"]["balance"] == 200


def test_transfer_to_another_customer():
    user_id, headers = make_customer()
    mine = open_account(headers, user_id, deposit=500)
    friend_id, friend = make_customer("Friend", "friend@example.com")
    theirs = open_account(friend, friend_id)
    res = client.post("/api/accounts/transfer", json={"fromAccountId": mine, "toAccountId": theirs, "amount": 100}, headers=headers)
    assert res.status_code == 200
    assert client.get(f"/api/accounts/{theirs}", headers=friend).json()["balance"] == 100


def test_cannot_transfer_from_someone_elses_account():
    victim_id, victim = make_customer("Victim", "victim@example.com")
    theirs = open_account(victim, victim_id, deposit=1000)
    user_id, headers = make_customer()
    mine = open_account(headers, user_id)
    res = client.post("/api/accounts/transfer", json={"fromAccountId": theirs, "toAccountId": mine, "amount": 500}, headers=headers)
    assert res.status_code == 403


def test_transfer_insufficient_funds():
    user_id, headers = make_customer()
    a = open_account(headers, user_id, deposit=100)
    b = open_account(headers, user_id)
    res = client.post("/api/accounts/transfer", json={"fromAccountId": a, "toAccountId": b, "amount": 500}, headers=headers)
    assert res.status_code == 400


def test_transfer_to_same_account():
    user_id, headers = make_customer()
    a = open_account(headers, user_id, deposit=100)
    res = client.post("/api/accounts/transfer", json={"fromAccountId": a, "toAccountId": a, "amount": 50}, headers=headers)
    assert res.status_code == 400


# ----- Audit -----

def test_audit_is_admin_only():
    _, headers = make_customer()
    assert client.get("/api/audit", headers=headers).status_code == 403


def test_deposit_audit_records_who():
    user_id, headers = make_customer()
    open_account(headers, user_id, deposit=500)
    _, admin = make_admin()
    log = client.get("/api/audit", headers=admin).json()[0]
    assert log["action"] == "DEPOSIT"
    assert log["status"] == "SUCCESS"
    assert log["performedByUserId"] == user_id
    assert log["performedByName"] == "Test User"
    assert log["amount"] == 500


def test_admin_action_is_audited_as_admin():
    user_id, headers = make_customer()
    account_id = open_account(headers, user_id)
    admin_id, admin = make_admin()
    client.post(f"/api/accounts/{account_id}/deposit", json={"amount": 100}, headers=admin)
    log = client.get("/api/audit", headers=admin).json()[0]
    assert log["performedByUserId"] == admin_id
    assert log["toAccountId"] == account_id


def test_failed_withdrawal_is_audited():
    user_id, headers = make_customer()
    account_id = open_account(headers, user_id, deposit=100)
    client.post(f"/api/accounts/{account_id}/withdraw", json={"amount": 500}, headers=headers)
    _, admin = make_admin()
    failed = client.get("/api/audit", params={"status": "FAILED"}, headers=admin).json()
    assert len(failed) == 1
    assert failed[0]["action"] == "WITHDRAW"
    assert "Insufficient funds" in failed[0]["reason"]


def test_transfer_audit_shows_both_accounts():
    user_id, headers = make_customer()
    a = open_account(headers, user_id, deposit=500)
    b = open_account(headers, user_id)
    client.post("/api/accounts/transfer", json={"fromAccountId": a, "toAccountId": b, "amount": 200}, headers=headers)
    _, admin = make_admin()
    log = client.get("/api/audit", params={"action": "TRANSFER"}, headers=admin).json()[0]
    assert log["fromAccountId"] == a
    assert log["toAccountId"] == b
    assert len(log["transactionIds"]) == 2


def test_trace_single_transaction():
    user_id, headers = make_customer()
    account_id = open_account(headers, user_id, deposit=250)
    txn_id = client.get(f"/api/accounts/{account_id}/transactions", headers=headers).json()[0]["transactionId"]
    _, admin = make_admin()
    res = client.get(f"/api/audit/transaction/{txn_id}", headers=admin)
    assert res.status_code == 200
    assert res.json()["action"] == "DEPOSIT"
    assert res.json()["amount"] == 250


def test_filter_audit_by_account():
    user_id, headers = make_customer()
    open_account(headers, user_id, deposit=100)
    second = open_account(headers, user_id, deposit=200)
    _, admin = make_admin()
    logs = client.get("/api/audit", params={"accountId": second}, headers=admin).json()
    assert len(logs) == 1
    assert logs[0]["toAccountId"] == second


def test_missing_audit_log_returns_404():
    _, admin = make_admin()
    assert client.get("/api/audit/999", headers=admin).status_code == 404
