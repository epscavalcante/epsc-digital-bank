from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.banking.domain.entities.ledger_entry import LedgerEntry
from app.banking.domain.enums.ledger_entry_type import LedgerEntryType
from app.banking.domain.repositories.ledger_entry_repository import (
    LedgerEntryRepository,
)
from app.banking.domain.value_objects.money import Money
from app.banking.infrastructure.repositories.ledger_entry_model import LedgerEntryModel


class LedgerEntryRepositoryImpl(LedgerEntryRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, ledger_entry: LedgerEntry) -> None:
        model = self._to_model(ledger_entry)
        self._session.merge(model)
        self._session.flush()

    def save_many(self, ledger_entries: list[LedgerEntry]) -> None:
        models = [self._to_model(ledger_entry) for ledger_entry in ledger_entries]
        self._session.add_all(models)
        self._session.flush()

    def find_by_id(self, ledger_entry_id: UUID) -> LedgerEntry | None:
        stmt = select(LedgerEntryModel).where(LedgerEntryModel.id == ledger_entry_id)
        model = self._session.scalar(stmt)
        if model is None:
            return None
        return self._to_entity(model)

    def find_by_transaction_id(self, transaction_id: UUID) -> list[LedgerEntry]:
        stmt = (
            select(LedgerEntryModel)
            .where(LedgerEntryModel.transaction_id == transaction_id)
            .order_by(LedgerEntryModel.created_at, LedgerEntryModel.id)
        )
        models = self._session.scalars(stmt).all()
        return [self._to_entity(model) for model in models]

    def find_by_account_id(self, account_id: UUID) -> list[LedgerEntry]:
        stmt = (
            select(LedgerEntryModel)
            .where(LedgerEntryModel.account_id == account_id)
            .order_by(LedgerEntryModel.created_at, LedgerEntryModel.id)
        )
        models = self._session.scalars(stmt).all()
        return [self._to_entity(model) for model in models]

    def _to_entity(self, model: LedgerEntryModel) -> LedgerEntry:
        return LedgerEntry(
            ledger_entry_id=model.id,
            transaction_id=model.transaction_id,
            account_id=model.account_id,
            entry_type=LedgerEntryType(model.entry_type),
            amount=Money(
                amount=Decimal(model.amount),
                currency=model.currency,
            ),
            created_at=model.created_at,
        )

    def _to_model(self, ledger_entry: LedgerEntry) -> LedgerEntryModel:
        return LedgerEntryModel(
            id=ledger_entry.id,
            transaction_id=ledger_entry.transaction_id,
            account_id=ledger_entry.account_id,
            entry_type=ledger_entry.entry_type.value,
            amount=str(ledger_entry.amount.amount),
            currency=ledger_entry.amount.currency,
            created_at=ledger_entry.created_at,
        )
