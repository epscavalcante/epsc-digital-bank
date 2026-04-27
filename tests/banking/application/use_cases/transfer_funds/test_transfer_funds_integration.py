from decimal import Decimal

import pytest

from app.banking.application.use_cases.transfer_funds.transfer_funds import TransferFunds
from app.banking.application.use_cases.transfer_funds.transfer_funds_input import (
    TransferFundsInput,
)
from app.banking.domain.entities.wallet import Wallet
from app.banking.domain.enums.ledger_entry_type import LedgerEntryType
from app.banking.domain.enums.transaction_type import TransactionType
from app.banking.domain.value_objects.money import Money
from app.identity.domain.entities.account import Account
from app.identity.infrastructure.database import Database
from app.shared.infrastructure.sqlalchemy_unit_of_work import SqlAlchemyUnitOfWork


class TestTransferFundsIntegration:
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
    def transfer_funds(self, unit_of_work):
        return TransferFunds(unit_of_work=unit_of_work)

    def test_transfer_funds_persists_wallets_transaction_and_ledger_entries(
        self,
        transfer_funds,
        unit_of_work,
    ):
        source_account = Account.create(
            name="John Doe",
            email="john@example.com",
            tax_id=self.VALID_CPF,
        )
        destination_account = Account.create(
            name="Jane Doe",
            email="jane@example.com",
            tax_id="11144477735",
        )
        source_wallet = Wallet.create(account_id=source_account.id)
        destination_wallet = Wallet.create(account_id=destination_account.id)
        source_wallet.deposit(Money(amount=Decimal("100.00")))

        with unit_of_work as setup_uow:
            setup_uow.account_repository.save(source_account)
            setup_uow.account_repository.save(destination_account)
            setup_uow.wallet_repository.save(source_wallet)
            setup_uow.wallet_repository.save(destination_wallet)
            setup_uow.commit()

        result = transfer_funds.execute(
            TransferFundsInput(
                source_wallet_id=source_wallet.id,
                destination_wallet_id=destination_wallet.id,
                amount=Money(amount=Decimal("25.00")),
                idempotency_key="transfer-int-001",
            )
        )

        with unit_of_work as verify_uow:
            saved_source_wallet = verify_uow.wallet_repository.find_by_id(source_wallet.id)
            saved_destination_wallet = verify_uow.wallet_repository.find_by_id(
                destination_wallet.id
            )
            saved_transaction = verify_uow.transaction_repository.find_by_id(
                result.transaction_id
            )
            saved_entries = verify_uow.ledger_entry_repository.find_by_transaction_id(
                result.transaction_id
            )

        assert saved_source_wallet is not None
        assert saved_destination_wallet is not None
        assert saved_source_wallet.balance.amount == Decimal("75.00")
        assert saved_destination_wallet.balance.amount == Decimal("25.00")

        assert saved_transaction is not None
        assert saved_transaction.type == TransactionType.TRANSFER
        assert saved_transaction.amount.amount == Decimal("25.00")
        assert saved_transaction.idempotency_key == "transfer-int-001"

        assert len(saved_entries) == 2
        assert {entry.entry_type for entry in saved_entries} == {
            LedgerEntryType.DEBIT,
            LedgerEntryType.CREDIT,
        }
        assert {entry.wallet_id for entry in saved_entries} == {
            source_wallet.id,
            destination_wallet.id,
        }
