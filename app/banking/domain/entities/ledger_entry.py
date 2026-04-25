from datetime import UTC, datetime
from uuid import UUID

from uuid6 import uuid7

from app.banking.domain.enums.ledger_entry_type import LedgerEntryType
from app.banking.domain.value_objects.money import Money


class LedgerEntry:
    def __init__(
        self,
        ledger_entry_id: UUID,
        transaction_id: UUID,
        wallet_id: UUID,
        entry_type: LedgerEntryType,
        amount: Money,
        created_at: datetime,
    ) -> None:
        self._ledger_entry_id = ledger_entry_id
        self._transaction_id = transaction_id
        self._wallet_id = wallet_id
        self._entry_type = entry_type
        self._amount = amount
        self._created_at = created_at

    @property
    def id(self) -> UUID:
        return self._ledger_entry_id

    @property
    def transaction_id(self) -> UUID:
        return self._transaction_id

    @property
    def wallet_id(self) -> UUID:
        return self._wallet_id

    @property
    def entry_type(self) -> LedgerEntryType:
        return self._entry_type

    @property
    def amount(self) -> Money:
        return self._amount

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @classmethod
    def create_credit(
        cls,
        transaction_id: UUID,
        wallet_id: UUID,
        amount: Money,
    ) -> "LedgerEntry":
        return cls(
            ledger_entry_id=uuid7(),
            transaction_id=transaction_id,
            wallet_id=wallet_id,
            entry_type=LedgerEntryType.CREDIT,
            amount=amount,
            created_at=datetime.now(UTC),
        )

    @classmethod
    def create_debit(
        cls,
        transaction_id: UUID,
        wallet_id: UUID,
        amount: Money,
    ) -> "LedgerEntry":
        return cls(
            ledger_entry_id=uuid7(),
            transaction_id=transaction_id,
            wallet_id=wallet_id,
            entry_type=LedgerEntryType.DEBIT,
            amount=amount,
            created_at=datetime.now(UTC),
        )
