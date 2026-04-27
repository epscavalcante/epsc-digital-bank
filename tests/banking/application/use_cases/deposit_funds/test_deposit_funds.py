from decimal import Decimal
from unittest.mock import MagicMock
from uuid import UUID, uuid4

import pytest

from app.banking.application.exceptions.invalid_deposit_amount_exception import (
    InvalidDepositAmountException,
)
from app.banking.application.use_cases.deposit_funds.deposit_funds import DepositFunds
from app.banking.application.use_cases.deposit_funds.deposit_funds_input import (
    DepositFundsInput,
)
from app.banking.application.use_cases.deposit_funds.deposit_funds_output import (
    DepositFundsOutput,
)
from app.banking.domain.entities.transaction import Transaction
from app.banking.domain.entities.wallet import Wallet
from app.banking.domain.enums.transaction_status import TransactionStatus
from app.banking.domain.enums.transaction_type import TransactionType
from app.banking.domain.exceptions.invalid_money_amount_exception import (
    InvalidMoneyAmountException,
)
from app.banking.domain.value_objects.money import Money
from app.identity.application.exceptions.account_not_found_exception import (
    AccountNotFoundException,
)


class TestDepositFunds:
    @pytest.fixture
    def mock_wallet_repository(self) -> MagicMock:
        mock = MagicMock()
        mock.find_by_id_for_update.return_value = None
        mock.save.return_value = None
        return mock

    @pytest.fixture
    def mock_transaction_repository(self) -> MagicMock:
        mock = MagicMock()
        mock.find_by_idempotency_key.return_value = None
        mock.save.return_value = None
        return mock

    @pytest.fixture
    def mock_ledger_entry_repository(self) -> MagicMock:
        mock = MagicMock()
        mock.save.return_value = None
        return mock

    @pytest.fixture
    def mock_unit_of_work(
        self,
        mock_wallet_repository: MagicMock,
        mock_transaction_repository: MagicMock,
        mock_ledger_entry_repository: MagicMock,
    ) -> MagicMock:
        mock = MagicMock()
        mock.wallet_repository = mock_wallet_repository
        mock.transaction_repository = mock_transaction_repository
        mock.ledger_entry_repository = mock_ledger_entry_repository
        mock.__enter__.return_value = mock
        mock.__exit__.return_value = None
        return mock

    @pytest.fixture
    def deposit_funds(self, mock_unit_of_work: MagicMock) -> DepositFunds:
        return DepositFunds(unit_of_work=mock_unit_of_work)

    @pytest.fixture
    def existing_wallet(self) -> Wallet:
        return Wallet.restore(
            wallet_id=UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
            account_id=UUID("12345678-1234-1234-1234-123456789012"),
            balance=Money(amount=Decimal("0.00")),
        )

    @pytest.fixture
    def create_wallet(self):
        def _create_wallet(balance: Decimal = Decimal("0.00")) -> Wallet:
            return Wallet.restore(
                wallet_id=uuid4(),
                account_id=uuid4(),
                balance=Money(amount=balance),
            )

        return _create_wallet

    def test_deposit_funds_creates_transaction_successfully(
        self,
        deposit_funds: DepositFunds,
        mock_wallet_repository: MagicMock,
        mock_transaction_repository: MagicMock,
        mock_ledger_entry_repository: MagicMock,
        existing_wallet: Wallet,
        mock_unit_of_work: MagicMock,
    ):
        mock_wallet_repository.find_by_id_for_update.return_value = existing_wallet

        input_data = DepositFundsInput(
            wallet_id=existing_wallet.id,
            amount=Money(amount=Decimal("100.00")),
        )
        result = deposit_funds.execute(input_data)

        assert isinstance(result, DepositFundsOutput)
        assert result.wallet_id == existing_wallet.id
        assert result.amount.amount == Decimal("100.00")
        assert result.transaction_type == TransactionType.DEPOSIT
        assert result.status == TransactionStatus.COMPLETED

        mock_wallet_repository.find_by_id_for_update.assert_called_once_with(
            existing_wallet.id
        )
        mock_wallet_repository.save.assert_called_once()
        mock_transaction_repository.save.assert_called_once()
        mock_ledger_entry_repository.save.assert_called_once()
        mock_unit_of_work.commit.assert_called_once()

    def test_deposit_funds_raises_exception_when_account_not_found(
        self,
        deposit_funds: DepositFunds,
        mock_wallet_repository: MagicMock,
        mock_unit_of_work: MagicMock,
    ):
        mock_wallet_repository.find_by_id_for_update.return_value = None

        input_data = DepositFundsInput(
            wallet_id=uuid4(),
            amount=Money(amount=Decimal("100.00")),
        )
        with pytest.raises(AccountNotFoundException):
            deposit_funds.execute(input_data)

        mock_wallet_repository.find_by_id_for_update.assert_called_once()
        mock_wallet_repository.save.assert_not_called()
        mock_unit_of_work.commit.assert_not_called()

    def test_deposit_funds_raises_exception_when_amount_is_zero(
        self,
        deposit_funds: DepositFunds,
        mock_wallet_repository: MagicMock,
        existing_wallet: Wallet,
        mock_unit_of_work: MagicMock,
    ):
        mock_wallet_repository.find_by_id_for_update.return_value = existing_wallet

        input_data = DepositFundsInput(
            wallet_id=existing_wallet.id,
            amount=Money(amount=Decimal("0.00")),
        )
        with pytest.raises(InvalidDepositAmountException):
            deposit_funds.execute(input_data)

        mock_wallet_repository.find_by_id_for_update.assert_called_once()
        mock_wallet_repository.save.assert_not_called()
        mock_unit_of_work.commit.assert_not_called()

    def test_deposit_funds_raises_exception_when_amount_is_negative(
        self,
        deposit_funds: DepositFunds,
        mock_wallet_repository: MagicMock,
        existing_wallet: Wallet,
    ):
        mock_wallet_repository.find_by_id_for_update.return_value = existing_wallet

        with pytest.raises(InvalidMoneyAmountException):
            Money(amount=Decimal("-100.00"))

    def test_deposit_funds_with_idempotency_key_returns_existing_transaction(
        self,
        deposit_funds: DepositFunds,
        mock_wallet_repository: MagicMock,
        mock_transaction_repository: MagicMock,
        mock_ledger_entry_repository: MagicMock,
        existing_wallet: Wallet,
        mock_unit_of_work: MagicMock,
    ):
        mock_wallet_repository.find_by_id_for_update.return_value = existing_wallet

        existing_transaction = Transaction(
            transaction_id=UUID("99999999-9999-9999-9999-999999999999"),
            transaction_type=TransactionType.DEPOSIT,
            transaction_status=TransactionStatus.COMPLETED,
            transaction_amount=Money(amount=Decimal("100.00")),
            payee_account_id=existing_wallet.account_id,
            idempotency_key="unique-key-123",
        )
        mock_transaction_repository.find_by_idempotency_key.return_value = (
            existing_transaction
        )

        input_data = DepositFundsInput(
            wallet_id=existing_wallet.id,
            amount=Money(amount=Decimal("100.00")),
            idempotency_key="unique-key-123",
        )
        result = deposit_funds.execute(input_data)
        assert isinstance(result, DepositFundsOutput)
        assert result.transaction_id == existing_transaction.id

        mock_wallet_repository.save.assert_not_called()
        mock_transaction_repository.save.assert_not_called()
        mock_ledger_entry_repository.save.assert_not_called()
        mock_unit_of_work.commit.assert_not_called()

    def test_deposit_funds_updates_wallet_balance(
        self,
        deposit_funds: DepositFunds,
        mock_wallet_repository: MagicMock,
        existing_wallet: Wallet,
    ):
        mock_wallet_repository.find_by_id_for_update.return_value = existing_wallet

        input_data = DepositFundsInput(
            wallet_id=existing_wallet.id,
            amount=Money(amount=Decimal("100.00")),
        )
        deposit_funds.execute(input_data)
        saved_wallet = mock_wallet_repository.save.call_args[0][0]
        assert saved_wallet.balance.amount == Decimal("100.00")

    def test_deposit_funds_creates_ledger_entry_with_credit_type(
        self,
        deposit_funds: DepositFunds,
        mock_wallet_repository: MagicMock,
        mock_ledger_entry_repository: MagicMock,
        existing_wallet: Wallet,
    ):
        mock_wallet_repository.find_by_id_for_update.return_value = existing_wallet

        input_data = DepositFundsInput(
            wallet_id=existing_wallet.id,
            amount=Money(amount=Decimal("100.00")),
        )
        deposit_funds.execute(input_data)
        ledger_entry = mock_ledger_entry_repository.save.call_args[0][0]
        assert ledger_entry.wallet_id == existing_wallet.id
        assert ledger_entry.amount.amount == Decimal("100.00")

    def test_deposit_funds_multiple_wallets_accumulate_balance_independently(
        self,
        deposit_funds: DepositFunds,
        mock_wallet_repository: MagicMock,
        create_wallet,
    ):
        wallet1 = create_wallet()
        wallet2 = create_wallet()

        mock_wallet_repository.find_by_id_for_update.return_value = wallet1
        input_data1 = DepositFundsInput(
            wallet_id=wallet1.id,
            amount=Money(amount=Decimal("100.00")),
        )
        result1 = deposit_funds.execute(input_data1)
        assert result1.amount.amount == Decimal("100.00")

        mock_wallet_repository.find_by_id_for_update.return_value = wallet2
        input_data2 = DepositFundsInput(
            wallet_id=wallet2.id,
            amount=Money(amount=Decimal("50.00")),
        )
        result2 = deposit_funds.execute(input_data2)
        assert result2.amount.amount == Decimal("50.00")
        assert mock_wallet_repository.save.call_count == 2
