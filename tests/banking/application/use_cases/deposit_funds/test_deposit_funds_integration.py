from decimal import Decimal

import pytest

from app.banking.application.use_cases.deposit_funds.deposit_funds import DepositFunds
from app.banking.application.use_cases.deposit_funds.deposit_funds_input import (
    DepositFundsInput,
)
from app.banking.domain.entities.wallet import Wallet
from app.banking.domain.enums.ledger_entry_type import LedgerEntryType
from app.banking.domain.enums.transaction_type import TransactionType
from app.banking.domain.value_objects.money import Money
from app.identity.domain.entities.account import Account
from app.identity.infrastructure.database import Database
from app.shared.infrastructure.sqlalchemy_unit_of_work import SqlAlchemyUnitOfWork


class TestDepositFundsIntegration:
    VALID_CPF = "52998224725"

    @pytest.fixture
    def database(self, tmp_path):
        db_path = tmp_path / "test.db"
        db = Database(f"sqlite:///{db_path}")
        db.create_tables()
        yield db
        db.drop_tables()
        db.dispose()

    @pytest.fixture
    def unit_of_work(self, database):
        return SqlAlchemyUnitOfWork(database)

    @pytest.fixture
    def deposit_funds(self, unit_of_work):
        return DepositFunds(unit_of_work=unit_of_work)

    def test_deposit_funds_persists_account_transaction_and_ledger_entry(
        self,
        deposit_funds,
        unit_of_work,
    ):
        account = Account.create(
            name="John Doe",
            email="john@example.com",
            tax_id=self.VALID_CPF,
        )
        wallet = Wallet.create(account_id=account.id)
        with unit_of_work as setup_uow:
            setup_uow.account_repository.save(account)
            setup_uow.wallet_repository.save(wallet)
            setup_uow.commit()

        result = deposit_funds.execute(
            DepositFundsInput(
                wallet_id=wallet.id,
                amount=Money(amount=Decimal("100.00")),
                idempotency_key="deposit-int-001",
            )
        )

        with unit_of_work as verify_uow:
            saved_wallet = verify_uow.wallet_repository.find_by_account_id(account.id)
            saved_transaction = verify_uow.transaction_repository.find_by_id(
                result.transaction_id
            )
            saved_entries = verify_uow.ledger_entry_repository.find_by_transaction_id(
                result.transaction_id
            )

        assert saved_wallet is not None
        assert saved_wallet.balance.amount == Decimal("100.00")

        assert saved_transaction is not None
        assert saved_transaction.type == TransactionType.DEPOSIT
        assert saved_transaction.amount.amount == Decimal("100.00")
        assert saved_transaction.idempotency_key == "deposit-int-001"

        assert len(saved_entries) == 1
        assert saved_entries[0].entry_type == LedgerEntryType.CREDIT
        assert saved_entries[0].amount.amount == Decimal("100.00")
        assert saved_entries[0].wallet_id == wallet.id

    def test_deposit_funds_reuses_existing_transaction_when_idempotency_key_repeats(
        self,
        deposit_funds,
        unit_of_work,
    ):
        account = Account.create(
            name="John Doe",
            email="john@example.com",
            tax_id=self.VALID_CPF,
        )
        wallet = Wallet.create(account_id=account.id)
        with unit_of_work as setup_uow:
            setup_uow.account_repository.save(account)
            setup_uow.wallet_repository.save(wallet)
            setup_uow.commit()

        first_result = deposit_funds.execute(
            DepositFundsInput(
                wallet_id=wallet.id,
                amount=Money(amount=Decimal("50.00")),
                idempotency_key="deposit-int-002",
            )
        )

        second_result = deposit_funds.execute(
            DepositFundsInput(
                wallet_id=wallet.id,
                amount=Money(amount=Decimal("50.00")),
                idempotency_key="deposit-int-002",
            )
        )

        with unit_of_work as verify_uow:
            saved_wallet = verify_uow.wallet_repository.find_by_account_id(account.id)
            saved_transaction = (
                verify_uow.transaction_repository.find_by_idempotency_key(
                    "deposit-int-002"
                )
            )
            saved_entries = verify_uow.ledger_entry_repository.find_by_wallet_id(
                wallet.id
            )

        assert first_result.transaction_id == second_result.transaction_id
        assert saved_wallet is not None
        assert saved_wallet.balance.amount == Decimal("50.00")
        assert saved_transaction is not None
        assert len(saved_entries) == 1

    def test_deposit_funds_rolls_back_all_changes_when_persistence_fails(
        self,
        database,
    ):
        class FailingSqlAlchemyUnitOfWork(SqlAlchemyUnitOfWork):
            def __enter__(self):
                super().__enter__()
                original_save = self.ledger_entry_repository.save

                def failing_save(ledger_entry):
                    original_save(ledger_entry)
                    raise RuntimeError("ledger failure")

                self.ledger_entry_repository.save = failing_save
                return self

        setup_uow = SqlAlchemyUnitOfWork(database)
        account = Account.create(
            name="John Doe",
            email="john@example.com",
            tax_id=self.VALID_CPF,
        )
        wallet = Wallet.create(account_id=account.id)
        with setup_uow as uow:
            uow.account_repository.save(account)
            uow.wallet_repository.save(wallet)
            uow.commit()

        failing_uow = FailingSqlAlchemyUnitOfWork(database)
        deposit_funds = DepositFunds(unit_of_work=failing_uow)

        with pytest.raises(RuntimeError, match="ledger failure"):
            deposit_funds.execute(
                DepositFundsInput(
                    wallet_id=wallet.id,
                    amount=Money(amount=Decimal("90.00")),
                    idempotency_key="deposit-int-003",
                )
            )

        verify_uow = SqlAlchemyUnitOfWork(database)
        with verify_uow as uow:
            saved_wallet = uow.wallet_repository.find_by_account_id(account.id)
            saved_transaction = uow.transaction_repository.find_by_idempotency_key(
                "deposit-int-003"
            )
            saved_entries = uow.ledger_entry_repository.find_by_wallet_id(wallet.id)

        assert saved_wallet is not None
        assert saved_wallet.balance.amount == Decimal("0.00")
        assert saved_transaction is None
        assert saved_entries == []
