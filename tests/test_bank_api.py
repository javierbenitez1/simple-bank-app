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