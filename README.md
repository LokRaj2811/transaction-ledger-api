# Transaction Ledger API

A RESTful transaction ledger API built using Python, FastAPI, SQLAlchemy, SQLite, and Pydantic.

## Features

- Create accounts with a unique ID and an initial balance of zero.
- Add credit and debit transactions.
- Prevent debit transactions when funds are insufficient.
- Reject duplicate reference IDs within the same account.
- Maintain account balances consistently with successful transactions.
- Retrieve account balances.
- View transaction history with transaction-type filtering and pagination.
- Sort transaction history by newest transaction first.
- Validate request data using Pydantic.
- Automated API tests using pytest.

## Technology Stack

- Python 3.13
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- Pytest
- HTTPX

## Project Structure

```text
transaction-ledger-api/
├── app/
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   └── schemas.py
├── tests/
│   ├── conftest.py
│   └── test_api.py
├── requirements.txt
├── ledger.db
└── README.md
```

## Setup

Create and activate a virtual environment, then install the dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Run the API

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Open the interactive API documentation:

http://127.0.0.1:8000/docs

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/accounts` | Create an account |
| GET | `/accounts/{account_id}/balance` | Retrieve an account balance |
| POST | `/accounts/{account_id}/transactions` | Create a credit or debit transaction |
| GET | `/accounts/{account_id}/transactions` | Retrieve transaction history |

### Transaction History Query Parameters

- `type`: Optional `credit` or `debit` filter.
- `page`: Page number, starting at 1.
- `limit`: Number of transactions per page, between 1 and 100.

## Run Tests

```powershell
.\.venv\Scripts\python.exe -m pytest -v
```

The automated tests cover account creation, balance updates, insufficient funds, duplicate references, transaction filtering, and pagination.
