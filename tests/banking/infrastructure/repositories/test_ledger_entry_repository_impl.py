from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID

import pytest

from app.banking.domain.entities.ledger_entry import LedgerEntry
from app.banking.domain.enums.ledger_entry_type import LedgerEntryType
from app.banking.domain.value_objects.money import Money
from app.banking.infrastructure.repositories.ledger_entry_repository_impl import (
    LedgerEntryRepositoryImpl,
)
from app.identity.infrastructure.database import Database


class TestLedgerEntryRepositoryImplIntegration:
    @pytest.fixture
    def database(self, tmp_path):
        db_path = tmp_path / "test.db"
        db = Database(f"sqlite:///{db_path}")
        db.create_tables()
        yield db
        db.drop_tables()
        db.dispose()

    @pytest.fixture
    def session(self, database):
        session = database.get_session()
        yield session
        session.close()

    @pytest.fixture
    def ledger_entry_repository(self, session):
        return LedgerEntryRepositoryImpl(session)

    def test_save_and_find_by_id(self, session, ledger_entry_repository):
        ledger_entry = LedgerEntry(
            ledger_entry_id=UUID("11111111-1111-1111-1111-111111111111"),
            transaction_id=UUID("22222222-2222-2222-2222-222222222222"),
            account_id=UUID("33333333-3333-3333-3333-333333333333"),
            entry_type=LedgerEntryType.CREDIT,
            amount=Money(amount=Decimal("100.00")),
            created_at=datetime.now(UTC),
        )

        ledger_entry_repository.save(ledger_entry)
        session.commit()

        saved_ledger_entry = ledger_entry_repository.find_by_id(ledger_entry.id)

        assert saved_ledger_entry is not None
        assert saved_ledger_entry.id == ledger_entry.id
        assert saved_ledger_entry.transaction_id == ledger_entry.transaction_id
        assert saved_ledger_entry.account_id == ledger_entry.account_id
        assert saved_ledger_entry.entry_type == LedgerEntryType.CREDIT
        assert saved_ledger_entry.amount.amount == Decimal("100.00")
        assert saved_ledger_entry.amount.currency == "BRL"

    def test_save_many_and_find_by_transaction_id(
        self,
        session,
        ledger_entry_repository,
    ):
        transaction_id = UUID("44444444-4444-4444-4444-444444444444")
        first_entry = LedgerEntry.create_credit(
            transaction_id=transaction_id,
            account_id=UUID("55555555-5555-5555-5555-555555555555"),
            amount=Money(amount=Decimal("75.00")),
        )
        second_entry = LedgerEntry.create_debit(
            transaction_id=transaction_id,
            account_id=UUID("66666666-6666-6666-6666-666666666666"),
            amount=Money(amount=Decimal("75.00")),
        )

        ledger_entry_repository.save_many([first_entry, second_entry])
        session.commit()

        saved_entries = ledger_entry_repository.find_by_transaction_id(transaction_id)

        assert len(saved_entries) == 2
        assert {entry.id for entry in saved_entries} == {
            first_entry.id,
            second_entry.id,
        }

    def test_find_by_account_id_returns_account_entries(
        self,
        session,
        ledger_entry_repository,
    ):
        account_id = UUID("77777777-7777-7777-7777-777777777777")
        first_entry = LedgerEntry.create_credit(
            transaction_id=UUID("88888888-8888-8888-8888-888888888888"),
            account_id=account_id,
            amount=Money(amount=Decimal("30.00")),
        )
        second_entry = LedgerEntry.create_credit(
            transaction_id=UUID("99999999-9999-9999-9999-999999999999"),
            account_id=account_id,
            amount=Money(amount=Decimal("40.00")),
        )
        third_entry = LedgerEntry.create_credit(
            transaction_id=UUID("aaaaaaaa-1111-1111-1111-111111111111"),
            account_id=UUID("bbbbbbbb-1111-1111-1111-111111111111"),
            amount=Money(amount=Decimal("50.00")),
        )

        ledger_entry_repository.save_many([first_entry, second_entry, third_entry])
        session.commit()

        saved_entries = ledger_entry_repository.find_by_account_id(account_id)

        assert len(saved_entries) == 2
        assert {entry.id for entry in saved_entries} == {
            first_entry.id,
            second_entry.id,
        }
