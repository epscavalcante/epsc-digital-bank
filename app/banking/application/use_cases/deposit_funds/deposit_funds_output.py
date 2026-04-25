from dataclasses import dataclass
from uuid import UUID

from app.banking.domain.enums.transaction_status import TransactionStatus
from app.banking.domain.enums.transaction_type import TransactionType
from app.banking.domain.value_objects.money import Money


@dataclass(frozen=True, slots=True)
class DepositFundsOutput:
    transaction_id: UUID
    wallet_id: UUID
    amount: Money
    transaction_type: TransactionType
    status: TransactionStatus
