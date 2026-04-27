from decimal import Decimal
from unittest.mock import MagicMock
from uuid import UUID, uuid4

import pytest

from app.banking.application.exceptions.invalid_transfer_amount_exception import (
    InvalidTransferAmountException,
)
from app.banking.application.exceptions.same_wallet_transfer_exception import (
    SameWalletTransferException,
)
from app.banking.application.use_cases.transfer_funds.transfer_funds import TransferFunds
from app.banking.application.use_cases.transfer_funds.transfer_funds_input import (
    TransferFundsInput,
)
from app.banking.application.use_cases.transfer_funds.transfer_funds_output import (
    TransferFundsOutput,
)
from app.banking.domain.entities.transaction import Transaction
from app.banking.domain.entities.wallet import Wallet
from app.banking.domain.enums.transaction_status import TransactionStatus
from app.banking.domain.enums.transaction_type import TransactionType
from app.banking.domain.exceptions.insufficient_funds_exception import (
    InsufficientFundsException,
)
from app.banking.domain.exceptions.invalid_money_amount_exception import (
    InvalidMoneyAmountException,
)
from app.banking.domain.value_objects.money import Money
from app.shared.domain.exceptions.not_found_exception import NotFoundException


class TestTransferFunds:
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
        mock.save_many.return_value = None
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
    def transfer_funds(self, mock_unit_of_work: MagicMock) -> TransferFunds:
        return TransferFunds(unit_of_work=mock_unit_of_work)

    @pytest.fixture
    def source_wallet(self) -> Wallet:
        return Wallet.restore(
            wallet_id=UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
            account_id=UUID("11111111-1111-1111-1111-111111111111"),
            balance=Money(amount=Decimal("100.00")),
        )

    @pytest.fixture
    def destination_wallet(self) -> Wallet:
        return Wallet.restore(
            wallet_id=UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"),
            account_id=UUID("22222222-2222-2222-2222-222222222222"),
            balance=Money(amount=Decimal("10.00")),
        )

    def test_transfer_funds_creates_transaction_successfully(
        self,
        transfer_funds: TransferFunds,
        mock_wallet_repository: MagicMock,
        mock_transaction_repository: MagicMock,
        mock_ledger_entry_repository: MagicMock,
        source_wallet: Wallet,
        destination_wallet: Wallet,
        mock_unit_of_work: MagicMock,
    ):
        mock_wallet_repository.find_by_id_for_update.side_effect = [
            source_wallet,
            destination_wallet,
        ]

        input_data = TransferFundsInput(
            source_wallet_id=source_wallet.id,
            destination_wallet_id=destination_wallet.id,
            amount=Money(amount=Decimal("25.00")),
        )
        result = transfer_funds.execute(input_data)

        assert isinstance(result, TransferFundsOutput)
        assert result.source_wallet_id == source_wallet.id
        assert result.destination_wallet_id == destination_wallet.id
        assert result.amount.amount == Decimal("25.00")
        assert result.transaction_type == TransactionType.TRANSFER
        assert result.status == TransactionStatus.COMPLETED

        assert mock_wallet_repository.save.call_count == 2
        mock_transaction_repository.save.assert_called_once()
        mock_ledger_entry_repository.save_many.assert_called_once()
        mock_unit_of_work.commit.assert_called_once()

    def test_transfer_funds_raises_when_source_wallet_not_found(
        self,
        transfer_funds: TransferFunds,
        mock_wallet_repository: MagicMock,
        mock_unit_of_work: MagicMock,
    ):
        mock_wallet_repository.find_by_id_for_update.side_effect = [None, None]

        input_data = TransferFundsInput(
            source_wallet_id=uuid4(),
            destination_wallet_id=uuid4(),
            amount=Money(amount=Decimal("25.00")),
        )

        with pytest.raises(NotFoundException, match="Wallet not found"):
            transfer_funds.execute(input_data)

        mock_unit_of_work.commit.assert_not_called()

    def test_transfer_funds_raises_when_destination_wallet_not_found(
        self,
        transfer_funds: TransferFunds,
        mock_wallet_repository: MagicMock,
        source_wallet: Wallet,
        mock_unit_of_work: MagicMock,
    ):
        mock_wallet_repository.find_by_id_for_update.side_effect = [source_wallet, None]

        input_data = TransferFundsInput(
            source_wallet_id=source_wallet.id,
            destination_wallet_id=uuid4(),
            amount=Money(amount=Decimal("25.00")),
        )

        with pytest.raises(NotFoundException, match="Wallet not found"):
            transfer_funds.execute(input_data)

        mock_unit_of_work.commit.assert_not_called()

    def test_transfer_funds_raises_when_amount_is_zero(
        self,
        transfer_funds: TransferFunds,
    ):
        input_data = TransferFundsInput(
            source_wallet_id=uuid4(),
            destination_wallet_id=uuid4(),
            amount=Money(amount=Decimal("0.00")),
        )

        with pytest.raises(InvalidTransferAmountException):
            transfer_funds.execute(input_data)

    def test_transfer_funds_raises_when_amount_is_negative(self):
        with pytest.raises(InvalidMoneyAmountException):
            Money(amount=Decimal("-1.00"))

    def test_transfer_funds_raises_when_wallets_are_the_same(
        self,
        transfer_funds: TransferFunds,
        source_wallet: Wallet,
    ):
        input_data = TransferFundsInput(
            source_wallet_id=source_wallet.id,
            destination_wallet_id=source_wallet.id,
            amount=Money(amount=Decimal("25.00")),
        )

        with pytest.raises(SameWalletTransferException):
            transfer_funds.execute(input_data)

    def test_transfer_funds_raises_when_source_wallet_has_insufficient_funds(
        self,
        transfer_funds: TransferFunds,
        mock_wallet_repository: MagicMock,
        source_wallet: Wallet,
        destination_wallet: Wallet,
        mock_unit_of_work: MagicMock,
    ):
        mock_wallet_repository.find_by_id_for_update.side_effect = [
            source_wallet,
            destination_wallet,
        ]

        input_data = TransferFundsInput(
            source_wallet_id=source_wallet.id,
            destination_wallet_id=destination_wallet.id,
            amount=Money(amount=Decimal("200.00")),
        )

        with pytest.raises(InsufficientFundsException):
            transfer_funds.execute(input_data)

        mock_unit_of_work.commit.assert_not_called()

    def test_transfer_funds_with_idempotency_key_returns_existing_transaction(
        self,
        transfer_funds: TransferFunds,
        mock_wallet_repository: MagicMock,
        mock_transaction_repository: MagicMock,
        source_wallet: Wallet,
        destination_wallet: Wallet,
    ):
        existing_transaction = Transaction(
            transaction_id=UUID("99999999-9999-9999-9999-999999999999"),
            transaction_type=TransactionType.TRANSFER,
            transaction_status=TransactionStatus.COMPLETED,
            transaction_amount=Money(amount=Decimal("25.00")),
            payer_account_id=source_wallet.account_id,
            payee_account_id=destination_wallet.account_id,
            idempotency_key="transfer-key-123",
        )
        mock_transaction_repository.find_by_idempotency_key.return_value = (
            existing_transaction
        )

        input_data = TransferFundsInput(
            source_wallet_id=source_wallet.id,
            destination_wallet_id=destination_wallet.id,
            amount=Money(amount=Decimal("25.00")),
            idempotency_key="transfer-key-123",
        )
        result = transfer_funds.execute(input_data)

        assert result.transaction_id == existing_transaction.id
        mock_wallet_repository.find_by_id_for_update.assert_not_called()
        mock_transaction_repository.save.assert_not_called()

    def test_transfer_funds_locks_wallets_in_stable_order(
        self,
        transfer_funds: TransferFunds,
        mock_wallet_repository: MagicMock,
        source_wallet: Wallet,
        destination_wallet: Wallet,
    ):
        # Use inverted lexical order to prove we lock consistently, not by request order.
        input_data = TransferFundsInput(
            source_wallet_id=destination_wallet.id,
            destination_wallet_id=source_wallet.id,
            amount=Money(amount=Decimal("5.00")),
        )
        mock_wallet_repository.find_by_id_for_update.side_effect = [
            source_wallet,
            destination_wallet,
        ]

        transfer_funds.execute(input_data)

        expected_order = sorted(
            [source_wallet.id, destination_wallet.id],
            key=str,
        )
        actual_order = [
            call.args[0] for call in mock_wallet_repository.find_by_id_for_update.call_args_list
        ]
        assert actual_order == expected_order
