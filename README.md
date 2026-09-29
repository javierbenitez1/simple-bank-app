# Simple Bank Application

A banking REST API built with Python and FastAPI that lets users create accounts, deposit and withdraw money, and view transaction history. The project is built in stages, and each stage lives on its own branch.

## Project Stages

| Stage | Branch | Storage | Description |
|-------|--------|---------|-------------|
| 1 | [`backend-no-db`](https://github.com/javierbenitez1/simple-bank-app/tree/backend-no-db) | In-memory | REST API with MVC layers, business rules, and tests |
| 2 | [`backend-with-db`](https://github.com/javierbenitez1/simple-bank-app/tree/backend-with-db) | MySQL | Same API backed by a relational database, with a SQL schema script |
| 2 | [`backend-with-mongodb`](https://github.com/javierbenitez1/simple-bank-app/tree/backend-with-mongodb) | MongoDB Atlas | Same API backed by a cloud document database |
| 3 | Coming soon | | React frontend |

Each branch has its own README with setup instructions. The code on `main` matches Stage 1.

## Why the Stages Matter

The app uses a layered architecture:

```
Controller (REST API) → Service (business logic) → Repository (data access) → Storage
```

Going from in-memory storage to MySQL to MongoDB only required rewriting the repository layer. The controllers, services, and business rules stayed exactly the same across all three versions, and the same test suite passes against each one.

## Tech Stack

- **Backend:** Python, FastAPI, Pydantic
- **Databases:** MySQL, MongoDB Atlas
- **Testing:** pytest, Postman
- **Tools:** Git, GitHub, VS Code, Swagger UI

## Business Rules

- Cannot withdraw more than the current balance
- Deposit and withdrawal amounts must be positive
- Every successful deposit and withdrawal is recorded as a transaction

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

Interactive API docs are available at `/docs` when the server is running.

## Postman Collection

The [`postman`](postman/) folder has a collection with every endpoint plus error cases (insufficient funds, negative deposit, missing account). Import it into Postman, start the server, and use **Run collection** to test the whole API. It works with all three backend versions.

## Quick Start (Stage 1)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Then open http://127.0.0.1:8000/docs.

## Author

**Javier Benitez** · [LinkedIn](https://linkedin.com/in/javi-benitez) · [GitHub](https://github.com/javierbenitez1)
