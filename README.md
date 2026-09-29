# Simple Bank Application: Backend REST API with MongoDB Atlas

A REST API built with Python and FastAPI that lets users create accounts, deposit and withdraw money, and view transaction history. Data is stored in MongoDB Atlas (cloud).

## Architecture

Follows MVC with a layered design:

```
Controller (REST API) → Service (business logic) → Repository (data access) → MongoDB Atlas
```

```
app/
├── controllers/    # REST endpoints
├── services/       # Business rules
├── repositories/   # MongoDB queries
├── models/         # Entities and request/response schemas
├── database.py     # Atlas connection and auto-increment ID counters
├── dependencies.py # Wires layers together
└── main.py         # App entry point and error handling
```

Only the repository layer and `database.py` differ from the in-memory and MySQL versions of this project. The controllers, services, and models are unchanged, which is the main benefit of the layered design.

## Collections

| Collection | Purpose |
|------------|---------|
| `users` | User name, email, and created date |
| `accounts` | Account type, balance, and owning user |
| `transactions` | Every deposit and withdrawal |
| `counters` | Generates simple integer IDs (1, 2, 3...) like SQL's AUTO_INCREMENT |

Money values are stored as `Decimal128` to avoid floating point rounding errors.

## Business Rules

- Cannot withdraw more than the current balance
- Deposit and withdrawal amounts must be positive
- Every successful deposit and withdrawal is recorded as a transaction

## Setup

**1. Create a free MongoDB Atlas cluster**

Sign up at mongodb.com/atlas, create a free M0 cluster, create a database user, allow your IP address, and copy the Python connection string.

**2. Configure the connection**

```bash
cp .env.example .env
```

Paste your connection string into `.env` and replace `<password>` with your database user's password.

**3. Run the app**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs to try the endpoints.

## Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/users` | Create a user |
| GET | `/api/users/{id}` | Get a user |
| POST | `/api/accounts` | Create an account |
| GET | `/api/accounts/{id}` | Get account details |
| POST | `/api/accounts/{id}/deposit` | Deposit money |
| POST | `/api/accounts/{id}/withdraw` | Withdraw money |
| GET | `/api/accounts/{id}/transactions` | View transaction history |

### Example

```bash
curl -X POST http://127.0.0.1:8000/api/accounts \
  -H "Content-Type: application/json" \
  -d '{"userId": 1, "accountType": "SAVINGS"}'
```

```json
{
  "accountId": 1,
  "userName": "Javier Benitez",
  "accountType": "SAVINGS",
  "balance": 0.0
}
```

## Tests

Tests run against a separate `simple_bank_test` database, so real data is never touched.

```bash
pytest -v
```
