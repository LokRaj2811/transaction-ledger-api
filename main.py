
from contextlib import asynccontextmanager
from decimal import Decimal, ROUND_HALF_UP
from math import ceil

from fastapi import Depends, FastAPI, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.models import Account, Transaction
from app.schemas import (
    AccountCreate,
    AccountResponse,
    TransactionCreate,
    TransactionResponse,
    TransactionHistoryResponse,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Transaction Ledger API",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/")
def root():
    return {"message": "Transaction Ledger API is running"}


@app.post(
    "/accounts",
    response_model=AccountResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_account(
    payload: AccountCreate,
    db: Session = Depends(get_db),
):
    account = Account(name=payload.name.strip())

    if not account.name:
        raise HTTPException(status_code=422, detail="Name cannot be blank")

    db.add(account)
    db.commit()
    db.refresh(account)
    return account


@app.get("/accounts/{account_id}/balance")
def get_balance(
    account_id: str,
    db: Session = Depends(get_db),
):
    account = db.get(Account, account_id)

    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")

    return {
    "account_id": account.id,
    "balance": account.balance,
}


@app.post(
    "/accounts/{account_id}/transactions",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_transaction(
    account_id: str,
    payload: TransactionCreate,
    db: Session = Depends(get_db),
):
    amount = payload.amount

    description = payload.description.strip()
    reference_id = payload.reference_id.strip()

    if not description or not reference_id:
        raise HTTPException(
            status_code=422,
            detail="Description and reference_id cannot be blank",
        )

    account = db.get(Account, account_id)

    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")

    try:
        # Start by checking for an existing reference.
        existing = db.scalar(
            select(Transaction).where(
                Transaction.account_id == account_id,
                Transaction.reference_id == reference_id,
            )
        )

        if existing is not None:
            raise HTTPException(
                status_code=409,
                detail="Duplicate reference_id for this account",
            )

        # Update the balance in the database itself.
        from sqlalchemy import update

        if payload.type == "credit":
            result = db.execute(
                update(Account)
                .where(Account.id == account_id)
                .values(balance=Account.balance + amount)
            )
        else:
            result = db.execute(
                update(Account)
                .where(
                    Account.id == account_id,
                    Account.balance >= amount,
                )
                .values(balance=Account.balance - amount)
            )

            if result.rowcount == 0:
                db.rollback()
                raise HTTPException(
                    status_code=400,
                    detail="Insufficient funds",
                )

        transaction = Transaction(
            account_id=account_id,
            type=payload.type,
            amount=amount,
            description=description,
            reference_id=reference_id,
        )

        db.add(transaction)
        db.commit()
        db.refresh(transaction)

        return transaction

    except HTTPException:
        if db.in_transaction():
            db.rollback()
        raise

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Duplicate reference_id for this account",
        )

    except Exception:
        db.rollback()
        raise


@app.get(
    "/accounts/{account_id}/transactions",
    response_model=TransactionHistoryResponse,
)
def transaction_history(
    account_id: str,
    transaction_type: str | None = Query(
        default=None,
        alias="type",
        pattern="^(credit|debit)$",
    ),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    account = db.get(Account, account_id)

    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")

    query = select(Transaction).where(Transaction.account_id == account_id)

    if transaction_type is not None:
        query = query.where(Transaction.type == transaction_type)

    

    from sqlalchemy import func

    count_query = select(func.count()).select_from(query.subquery())
    total_records = db.scalar(count_query) or 0

    transactions = db.scalars(
        query.order_by(Transaction.created_at.desc(), Transaction.id.desc())
        .offset((page - 1) * limit)
        .limit(limit)
    ).all()

    return {
        "items": transactions,
        "page": page,
        "limit": limit,
        "total_records": total_records,
        "total_pages": ceil(total_records / limit) if total_records else 0,
    }
