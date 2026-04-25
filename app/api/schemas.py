from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ErrorResponse(BaseModel):
    detail: str


class HealthResponse(BaseModel):
    status: str


class SignupRequest(BaseModel):
    tax_id: str
    name: str
    email: str


class SignupResponse(BaseModel):
    account_id: UUID


class DepositFundsRequest(BaseModel):
    amount: Decimal


class MoneyResponse(BaseModel):
    amount: Decimal
    currency: str

    model_config = ConfigDict(from_attributes=True)


class DepositFundsResponse(BaseModel):
    transaction_id: UUID
    wallet_id: UUID
    amount: MoneyResponse
    transaction_type: str
    status: str
