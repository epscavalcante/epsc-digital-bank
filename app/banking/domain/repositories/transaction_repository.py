from typing import Protocol
from uuid import UUID

from app.banking.domain.entities.transaction import Transaction


class TransactionRepository(Protocol):
    def find_by_id(self, transaction_id: UUID) -> Transaction | None: ...
    def find_by_idempotency_key(
        self,
        idempotency_key: str,
    ) -> Transaction | None: ...
    def save(self, transaction: Transaction) -> None: ...
