from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from app.banking.domain.entities.ledger_entry import LedgerEntry
from app.banking.domain.enums.ledger_entry_type import LedgerEntryType
from app.banking.domain.value_objects.money import Money


class TestLedgerEntry:
    def test_create_credit_generates_uuid(self):
        transaction_id = uuid4()
        account_id = uuid4()
        amount = Money(amount=Decimal("100.00"))

        entry = LedgerEntry.create_credit(
            transaction_id=transaction_id,
            account_id=account_id,
            amount=amount,
        )

        assert isinstance(entry._ledger_entry_id, UUID)

    def test_create_credit_with_valid_data(self):
        transaction_id = uuid4()
        account_id = uuid4()
        amount = Money(amount=Decimal("100.00"))

        entry = LedgerEntry.create_credit(
            transaction_id=transaction_id,
            account_id=account_id,
            amount=amount,
        )

        assert entry.transaction_id == transaction_id
        assert entry.account_id == account_id
        assert entry.entry_type == LedgerEntryType.CREDIT
        assert entry.amount == amount

    def test_create_debit_generates_uuid(self):
        transaction_id = uuid4()
        account_id = uuid4()
        amount = Money(amount=Decimal("50.00"))

        entry = LedgerEntry.create_debit(
            transaction_id=transaction_id,
            account_id=account_id,
            amount=amount,
        )

        assert isinstance(entry._ledger_entry_id, UUID)

    def test_create_debit_with_valid_data(self):
        transaction_id = uuid4()
        account_id = uuid4()
        amount = Money(amount=Decimal("50.00"))

        entry = LedgerEntry.create_debit(
            transaction_id=transaction_id,
            account_id=account_id,
            amount=amount,
        )

        assert entry.transaction_id == transaction_id
        assert entry.account_id == account_id
        assert entry.entry_type == LedgerEntryType.DEBIT
        assert entry.amount == amount

    def test_ledger_entry_has_private_attributes(self):
        transaction_id = uuid4()
        account_id = uuid4()
        amount = Money(amount=Decimal("100.00"))

        entry = LedgerEntry.create_credit(
            transaction_id=transaction_id,
            account_id=account_id,
            amount=amount,
        )

        assert hasattr(entry, "_ledger_entry_id")
        assert hasattr(entry, "_transaction_id")
        assert hasattr(entry, "_account_id")
        assert hasattr(entry, "_entry_type")
        assert hasattr(entry, "_amount")
        assert hasattr(entry, "_created_at")

    def test_ledger_entry_id_property(self):
        transaction_id = uuid4()
        account_id = uuid4()
        amount = Money(amount=Decimal("100.00"))

        entry = LedgerEntry.create_credit(
            transaction_id=transaction_id,
            account_id=account_id,
            amount=amount,
        )

        assert entry.id == entry._ledger_entry_id

    def test_ledger_entry_created_at_is_datetime(self):
        transaction_id = uuid4()
        account_id = uuid4()
        amount = Money(amount=Decimal("100.00"))

        entry = LedgerEntry.create_credit(
            transaction_id=transaction_id,
            account_id=account_id,
            amount=amount,
        )

        assert isinstance(entry.created_at, datetime)

    def test_ledger_entry_credit_type_is_credit(self):
        transaction_id = uuid4()
        account_id = uuid4()
        amount = Money(amount=Decimal("100.00"))

        entry = LedgerEntry.create_credit(
            transaction_id=transaction_id,
            account_id=account_id,
            amount=amount,
        )

        assert entry.entry_type == LedgerEntryType.CREDIT

    def test_ledger_entry_debit_type_is_debit(self):
        transaction_id = uuid4()
        account_id = uuid4()
        amount = Money(amount=Decimal("100.00"))

        entry = LedgerEntry.create_debit(
            transaction_id=transaction_id,
            account_id=account_id,
            amount=amount,
        )

        assert entry.entry_type == LedgerEntryType.DEBIT
