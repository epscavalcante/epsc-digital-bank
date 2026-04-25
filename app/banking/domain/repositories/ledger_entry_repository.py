from typing import Protocol
from uuid import UUID

from app.banking.domain.entities.ledger_entry import LedgerEntry


class LedgerEntryRepository(Protocol):
    def save(
        self,
        ledger_entry: LedgerEntry,
    ) -> None: ...

    def save_many(
        self,
        ledger_entries: list[LedgerEntry],
    ) -> None: ...

    def find_by_id(
        self,
        ledger_entry_id: UUID,
    ) -> LedgerEntry | None: ...

    def find_by_transaction_id(
        self,
        transaction_id: UUID,
    ) -> list[LedgerEntry]: ...

    def find_by_wallet_id(
        self,
        wallet_id: UUID,
    ) -> list[LedgerEntry]: ...
