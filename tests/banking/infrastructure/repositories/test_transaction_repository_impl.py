from decimal import Decimal
from uuid import UUID

import pytest

from app.banking.domain.entities.transaction import Transaction
from app.banking.domain.enums.transaction_status import TransactionStatus
from app.banking.domain.enums.transaction_type import TransactionType
from app.banking.domain.value_objects.money import Money
from app.banking.infrastructure.repositories.transaction_repository_impl import (
    TransactionRepositoryImpl,
)
from app.identity.infrastructure.database import Database


class TestTransactionRepositoryImplIntegration:
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
    def transaction_repository(self, session):
        return TransactionRepositoryImpl(session)

    def test_save_and_find_by_id(self, session, transaction_repository):
        transaction = Transaction(
            transaction_id=UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
            transaction_type=TransactionType.DEPOSIT,
            transaction_status=TransactionStatus.COMPLETED,
            transaction_amount=Money(amount=Decimal("150.00")),
            payee_account_id=UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"),
            idempotency_key="deposit-001",
        )

        transaction_repository.save(transaction)
        session.commit()

        saved_transaction = transaction_repository.find_by_id(transaction.id)

        assert saved_transaction is not None
        assert saved_transaction.id == transaction.id
        assert saved_transaction.type == TransactionType.DEPOSIT
        assert saved_transaction.status == TransactionStatus.COMPLETED
        assert saved_transaction.amount.amount == Decimal("150.00")
        assert saved_transaction.amount.currency == "BRL"
        assert saved_transaction.payee_account_id == transaction.payee_account_id
        assert saved_transaction.idempotency_key == "deposit-001"

    def test_find_by_idempotency_key_returns_transaction(
        self,
        session,
        transaction_repository,
    ):
        transaction = Transaction(
            transaction_id=UUID("cccccccc-cccc-cccc-cccc-cccccccccccc"),
            transaction_type=TransactionType.DEPOSIT,
            transaction_status=TransactionStatus.COMPLETED,
            transaction_amount=Money(amount=Decimal("80.00")),
            payee_account_id=UUID("dddddddd-dddd-dddd-dddd-dddddddddddd"),
            idempotency_key="deposit-002",
        )

        transaction_repository.save(transaction)
        session.commit()

        saved_transaction = transaction_repository.find_by_idempotency_key(
            "deposit-002"
        )

        assert saved_transaction is not None
        assert saved_transaction.id == transaction.id
        assert saved_transaction.amount.amount == Decimal("80.00")

    def test_find_by_id_returns_none_when_transaction_does_not_exist(
        self,
        transaction_repository,
    ):
        saved_transaction = transaction_repository.find_by_id(
            UUID("eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee")
        )

        assert saved_transaction is None
