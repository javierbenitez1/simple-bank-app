import os
os.environ["MONGODB_DB_NAME"] = "simple_bank_test"

import pytest
from fastapi.testclient import TestClient

from app.dependencies import reset_data
from app.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_data():
    reset_data()


def create_user_and_account():
    client.post("/api/users", json={"name": "Test User", "email": "test@example.com"})
    return client.post("/api/accounts", json={"userId": 1, "accountType": "SAVINGS"}).json()


def test_create_account():
    account = create_user_and_account()
    assert account["accountId"] == 1
    assert account["userName"] == "Test User"
    assert account["balance"] == 0


def test_create_account_for_missing_user_returns_404():
    res = client.post("/api/accounts", json={"userId": 99, "accountType": "SAVINGS"})
    assert res.status_code == 404


def test_get_missing_account_returns_404():
    assert client.get("/api/accounts/99").status_code == 404


def test_deposit_increases_balance():
    create_user_and_account()
    res = client.post("/api/accounts/1/deposit", json={"amount": 500})
    assert res.status_code == 200
    assert res.json()["balance"] == 500


def test_deposit_must_be_positive():
    create_user_and_account()
    res = client.post("/api/accounts/1/deposit", json={"amount": -50})
    assert res.status_code == 400


def test_withdraw_decreases_balance():
    create_user_and_account()
    client.post("/api/accounts/1/deposit", json={"amount": 500})
    res = client.post("/api/accounts/1/withdraw", json={"amount": 200})
    assert res.json()["balance"] == 300


def test_cannot_withdraw_more_than_balance():
    create_user_and_account()
    client.post("/api/accounts/1/deposit", json={"amount": 100})
    res = client.post("/api/accounts/1/withdraw", json={"amount": 500})
    assert res.status_code == 400
    assert client.get("/api/accounts/1").json()["balance"] == 100


def test_transactions_are_recorded():
    create_user_and_account()
    client.post("/api/accounts/1/deposit", json={"amount": 500})
    client.post("/api/accounts/1/withdraw", json={"amount": 200})
    client.post("/api/accounts/1/withdraw", json={"amount": 9999})  # fails, should not be recorded
    txns = client.get("/api/accounts/1/transactions").json()
    assert [t["type"] for t in txns] == ["DEPOSIT", "WITHDRAW"]
    assert [t["amount"] for t in txns] == [500, 200]


def test_duplicate_email_returns_409():
    client.post("/api/users", json={"name": "A", "email": "same@example.com"})
    res = client.post("/api/users", json={"name": "B", "email": "same@example.com"})
    assert res.status_code == 409


def test_invalid_account_type_returns_422():
    client.post("/api/users", json={"name": "A", "email": "a@example.com"})
    res = client.post("/api/accounts", json={"userId": 1, "accountType": "CRYPTO"})
    assert res.status_code == 422

def test_list_users():
    client.post("/api/users", json={"name": "A", "email": "a@example.com"})
    client.post("/api/users", json={"name": "B", "email": "b@example.com"})
    assert [u["name"] for u in client.get("/api/users").json()] == ["A", "B"]


def test_update_user():
    client.post("/api/users", json={"name": "Old Name", "email": "old@example.com"})
    res = client.put("/api/users/1", json={"name": "New Name"})
    assert res.status_code == 200
    assert res.json()["name"] == "New Name"
    assert res.json()["email"] == "old@example.com"


def test_update_user_to_taken_email_returns_409():
    client.post("/api/users", json={"name": "A", "email": "a@example.com"})
    client.post("/api/users", json={"name": "B", "email": "b@example.com"})
    assert client.put("/api/users/2", json={"email": "a@example.com"}).status_code == 409


def test_delete_user():
    client.post("/api/users", json={"name": "Temp", "email": "temp@example.com"})
    assert client.delete("/api/users/1").status_code == 204
    assert client.get("/api/users/1").status_code == 404


def test_cannot_delete_user_with_accounts():
    create_user_and_account()
    assert client.delete("/api/users/1").status_code == 409


# ----- Priority 2: Accounts -----

def setup_two_accounts(balance_1=0, balance_2=0):
    client.post("/api/users", json={"name": "Test User", "email": "test@example.com"})
    client.post("/api/accounts", json={"userId": 1, "accountType": "SAVINGS"})
    client.post("/api/accounts", json={"userId": 1, "accountType": "CHECKING"})
    if balance_1:
        client.post("/api/accounts/1/deposit", json={"amount": balance_1})
    if balance_2:
        client.post("/api/accounts/2/deposit", json={"amount": balance_2})


def test_list_all_accounts():
    setup_two_accounts()
    assert len(client.get("/api/accounts").json()) == 2


def test_customer_has_many_accounts():
    setup_two_accounts()
    accounts = client.get("/api/users/1/accounts").json()
    assert [a["accountType"] for a in accounts] == ["SAVINGS", "CHECKING"]


def test_premium_accounts():
    setup_two_accounts(balance_1=500, balance_2=2000)
    premium = client.get("/api/accounts/premium", params={"threshold": 1000}).json()
    assert [a["accountId"] for a in premium] == [2]


def test_update_account_type():
    create_user_and_account()
    res = client.put("/api/accounts/1", json={"accountType": "CHECKING"})
    assert res.status_code == 200
    assert res.json()["accountType"] == "CHECKING"


def test_delete_empty_account():
    create_user_and_account()
    assert client.delete("/api/accounts/1").status_code == 204
    assert client.get("/api/accounts/1").status_code == 404


def test_cannot_delete_account_with_balance():
    create_user_and_account()
    client.post("/api/accounts/1/deposit", json={"amount": 100})
    assert client.delete("/api/accounts/1").status_code == 409


def test_transfer_between_accounts():
    setup_two_accounts(balance_1=500)
    res = client.post("/api/accounts/transfer", json={"fromAccountId": 1, "toAccountId": 2, "amount": 200})
    assert res.status_code == 200
    assert res.json()["fromAccount"]["balance"] == 300
    assert res.json()["toAccount"]["balance"] == 200
    assert client.get("/api/accounts/1/transactions").json()[-1]["type"] == "TRANSFER_OUT"
    assert client.get("/api/accounts/2/transactions").json()[-1]["type"] == "TRANSFER_IN"


def test_transfer_insufficient_funds():
    setup_two_accounts(balance_1=100)
    res = client.post("/api/accounts/transfer", json={"fromAccountId": 1, "toAccountId": 2, "amount": 500})
    assert res.status_code == 400


def test_transfer_to_same_account():
    setup_two_accounts(balance_1=100)
    res = client.post("/api/accounts/transfer", json={"fromAccountId": 1, "toAccountId": 1, "amount": 50})
    assert res.status_code == 400


# ----- Priority 3: Audit trail -----

def test_deposit_creates_audit_log():
    create_user_and_account()
    client.post("/api/accounts/1/deposit", json={"amount": 500})
    logs = client.get("/api/audit").json()
    assert len(logs) == 1
    log = logs[0]
    assert log["action"] == "DEPOSIT"
    assert log["status"] == "SUCCESS"
    assert log["performedByName"] == "Test User"
    assert log["toAccountId"] == 1
    assert log["amount"] == 500
    assert log["transactionIds"] == [1]


def test_failed_withdrawal_is_audited():
    create_user_and_account()
    client.post("/api/accounts/1/deposit", json={"amount": 100})
    client.post("/api/accounts/1/withdraw", json={"amount": 500})
    failed = client.get("/api/audit", params={"status": "FAILED"}).json()
    assert len(failed) == 1
    assert failed[0]["action"] == "WITHDRAW"
    assert "Insufficient funds" in failed[0]["reason"]


def test_transfer_audit_shows_both_accounts():
    setup_two_accounts(balance_1=500)
    client.post("/api/accounts/transfer", json={"fromAccountId": 1, "toAccountId": 2, "amount": 200})
    log = client.get("/api/audit", params={"action": "TRANSFER"}).json()[0]
    assert log["fromAccountId"] == 1
    assert log["toAccountId"] == 2
    assert log["performedByUserId"] == 1
    assert len(log["transactionIds"]) == 2


def test_trace_single_transaction():
    create_user_and_account()
    client.post("/api/accounts/1/deposit", json={"amount": 250})
    res = client.get("/api/audit/transaction/1")
    assert res.status_code == 200
    assert res.json()["action"] == "DEPOSIT"
    assert res.json()["amount"] == 250


def test_filter_audit_by_account():
    setup_two_accounts(balance_1=100, balance_2=200)
    logs = client.get("/api/audit", params={"accountId": 2}).json()
    assert len(logs) == 1
    assert logs[0]["toAccountId"] == 2


def test_missing_audit_log_returns_404():
    assert client.get("/api/audit/999").status_code == 404
