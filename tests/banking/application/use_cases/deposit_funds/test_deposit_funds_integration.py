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
from app.banking.infrastructure.repositories.ledger_entry_repository_impl import (
    LedgerEntryRepositoryImpl,
)
from app.banking.infrastructure.repositories.transaction_repository_impl import (
    TransactionRepositoryImpl,
)
from app.banking.infrastructure.repositories.wallet_repository_impl import (
    WalletRepositoryImpl,
)
from app.identity.domain.entities.account import Account
from app.identity.infrastructure.database import Database
from app.identity.infrastructure.repositories.account_repository_impl import (
    AccountRepositoryImpl,
)
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
    def session(self, database):
        session = database.get_session()
        yield session
        session.close()

    @pytest.fixture
    def unit_of_work(self, session):
        return SqlAlchemyUnitOfWork(session)

    @pytest.fixture
    def account_repository(self, session):
        return AccountRepositoryImpl(session)

    @pytest.fixture
    def wallet_repository(self, session):
        return WalletRepositoryImpl(session)

    @pytest.fixture
    def transaction_repository(self, session):
        return TransactionRepositoryImpl(session)

    @pytest.fixture
    def ledger_entry_repository(self, session):
        return LedgerEntryRepositoryImpl(session)

    @pytest.fixture
    def deposit_funds(
        self,
        unit_of_work,
        wallet_repository,
        transaction_repository,
        ledger_entry_repository,
    ):
        return DepositFunds(
            unit_of_work=unit_of_work,
            wallet_repository=wallet_repository,
            transaction_repository=transaction_repository,
            ledger_entry_repository=ledger_entry_repository,
        )

    def test_deposit_funds_persists_account_transaction_and_ledger_entry(
        self,
        deposit_funds,
        unit_of_work,
        account_repository,
        wallet_repository,
        transaction_repository,
        ledger_entry_repository,
    ):
        account = Account.create(
            name="John Doe",
            email="john@example.com",
            tax_id=self.VALID_CPF,
        )
        wallet = Wallet.create(account_id=account.id)
        with unit_of_work as uow:
            account_repository.save(account)
            wallet_repository.save(wallet)
            uow.commit()

        result = deposit_funds.execute(
            DepositFundsInput(
                wallet_id=wallet.id,
                amount=Money(amount=Decimal("100.00")),
                idempotency_key="deposit-int-001",
            )
        )

        with unit_of_work:
            saved_wallet = wallet_repository.find_by_account_id(account.id)
            saved_transaction = transaction_repository.find_by_id(result.transaction_id)
            saved_entries = ledger_entry_repository.find_by_transaction_id(
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
        account_repository,
        wallet_repository,
        transaction_repository,
        ledger_entry_repository,
    ):
        account = Account.create(
            name="John Doe",
            email="john@example.com",
            tax_id=self.VALID_CPF,
        )
        wallet = Wallet.create(account_id=account.id)
        with unit_of_work as uow:
            account_repository.save(account)
            wallet_repository.save(wallet)
            uow.commit()

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

        with unit_of_work:
            saved_wallet = wallet_repository.find_by_account_id(account.id)
            saved_transaction = transaction_repository.find_by_idempotency_key(
                "deposit-int-002"
            )
            saved_entries = ledger_entry_repository.find_by_wallet_id(wallet.id)

        assert first_result.transaction_id == second_result.transaction_id
        assert saved_wallet is not None
        assert saved_wallet.balance.amount == Decimal("50.00")
        assert saved_transaction is not None
        assert len(saved_entries) == 1

    def test_deposit_funds_rolls_back_all_changes_when_persistence_fails(
        self,
        session,
    ):
        class FailingLedgerEntryRepository(LedgerEntryRepositoryImpl):
            def save(self, ledger_entry):
                super().save(ledger_entry)
                raise RuntimeError("ledger failure")

        setup_uow = SqlAlchemyUnitOfWork(session)
        account_repository = AccountRepositoryImpl(session)
        wallet_repository = WalletRepositoryImpl(session)
        transaction_repository = TransactionRepositoryImpl(session)
        ledger_entry_repository = LedgerEntryRepositoryImpl(session)
        account = Account.create(
            name="John Doe",
            email="john@example.com",
            tax_id=self.VALID_CPF,
        )
        wallet = Wallet.create(account_id=account.id)
        with setup_uow as uow:
            account_repository.save(account)
            wallet_repository.save(wallet)
            uow.commit()

        failing_uow = SqlAlchemyUnitOfWork(session)
        deposit_funds = DepositFunds(
            unit_of_work=failing_uow,
            wallet_repository=wallet_repository,
            transaction_repository=transaction_repository,
            ledger_entry_repository=FailingLedgerEntryRepository(session),
        )

        with pytest.raises(RuntimeError, match="ledger failure"):
            deposit_funds.execute(
                DepositFundsInput(
                    wallet_id=wallet.id,
                    amount=Money(amount=Decimal("90.00")),
                    idempotency_key="deposit-int-003",
                )
            )

        verify_uow = SqlAlchemyUnitOfWork(session)
        with verify_uow:
            saved_wallet = wallet_repository.find_by_account_id(account.id)
            saved_transaction = transaction_repository.find_by_idempotency_key(
                "deposit-int-003"
            )
            saved_entries = ledger_entry_repository.find_by_wallet_id(wallet.id)

        assert saved_wallet is not None
        assert saved_wallet.balance.amount == Decimal("0.00")
        assert saved_transaction is None
        assert saved_entries == []
