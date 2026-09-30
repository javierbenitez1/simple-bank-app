# Simple Bank Application: Backend REST API with MySQL

Stage 2 of the Simple Bank Application project. A REST API built with Python and FastAPI that lets users create accounts, deposit and withdraw money, and view transaction history. Data is stored in a MySQL database.

## Architecture

Follows MVC with a layered design:

```
Controller (REST API) → Service (business logic) → Repository (data access) → MySQL
```

```
app/
├── controllers/    # REST endpoints
├── services/       # Business rules
├── repositories/   # SQL queries against MySQL
├── models/         # Entities and request/response schemas
├── database.py     # MySQL connection handling
├── dependencies.py # Wires layers together
└── main.py         # App entry point and error handling
sql/
└── schema.sql      # Creates the users, accounts, and transactions tables
```

## Business Rules

- Cannot withdraw more than the current balance
- Deposit and withdrawal amounts must be positive
- Every successful deposit and withdrawal is recorded as a transaction
- Rules are enforced in the service layer and backed by database constraints

## Setup

**1. Install MySQL and create the databases**

```bash
brew install mysql
brew services start mysql
mysql -u root
```

```sql
CREATE DATABASE simple_bank;
CREATE DATABASE simple_bank_test;
CREATE USER 'bank_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON simple_bank.* TO 'bank_user'@'localhost';
GRANT ALL PRIVILEGES ON simple_bank_test.* TO 'bank_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

**2. Create the tables**

```bash
mysql -u bank_user -p simple_bank < sql/schema.sql
mysql -u bank_user -p simple_bank_test < sql/schema.sql
```

**3. Configure the connection**

```bash
cp .env.example .env
```

Then fill in your MySQL username and password in `.env`.

**4. Run the app**

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

Tests run against the separate `simple_bank_test` database, so your real data is never touched.

```bash
pytest -v
```
