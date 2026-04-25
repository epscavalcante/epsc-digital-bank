from dataclasses import dataclass
from uuid import UUID

from app.banking.domain.value_objects.money import Money


@dataclass(frozen=True, slots=True)
class DepositFundsInput:
    wallet_id: UUID
    amount: Money
    idempotency_key: str | None = None
