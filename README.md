# Simple Bank Application: Backend REST API (No Database)

Stage 1 of the Simple Bank Application project. A REST API built with Python and FastAPI that lets users create accounts, deposit and withdraw money, and view transaction history. Data is stored in memory for this stage, so it resets when the server restarts.

## Architecture

Follows MVC with a layered design:

```
Controller (REST API) → Service (business logic) → Repository (data access) → In-memory storage
```

```
app/
├── controllers/    # REST endpoints
├── services/       # Business rules
├── repositories/   # Data storage (swapped for MySQL in Stage 2)
├── models/         # Entities and request/response schemas
├── dependencies.py # Wires layers together
└── main.py         # App entry point and error handling
```

## Business Rules

- Cannot withdraw more than the current balance
- Deposit and withdrawal amounts must be positive
- Every successful deposit and withdrawal is recorded as a transaction

## Run It

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Then open http://127.0.0.1:8000/docs to try the endpoints.

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

```bash
pytest -v
```