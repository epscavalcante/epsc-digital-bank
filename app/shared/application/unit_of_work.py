from typing import Protocol, Self

from app.banking.domain.repositories.ledger_entry_repository import (
    LedgerEntryRepository,
)
from app.banking.domain.repositories.transaction_repository import (
    TransactionRepository,
)
from app.identity.domain.repositories.account_repository import AccountRepository


class UnitOfWork(Protocol):
    account_repository: AccountRepository
    transaction_repository: TransactionRepository
    ledger_entry_repository: LedgerEntryRepository

    def __enter__(self) -> Self: ...
    def __exit__(self, exc_type, exc_value, traceback) -> None: ...
    def commit(self) -> None: ...
    def rollback(self) -> None: ...
