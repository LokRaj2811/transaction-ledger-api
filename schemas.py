
from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class AccountCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class AccountResponse(BaseModel):
    id: str
    name: str
    balance: Decimal
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TransactionCreate(BaseModel):
    type: Literal["credit", "debit"]
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    description: str = Field(min_length=1, max_length=255)
    reference_id: str = Field(min_length=1, max_length=100)


class TransactionResponse(BaseModel):
    id: str
    account_id: str
    type: Literal["credit", "debit"]
    amount: Decimal
    description: str
    reference_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TransactionHistoryResponse(BaseModel):
    items: list[TransactionResponse]
    page: int
    limit: int
    total_records: int
    total_pages: int
