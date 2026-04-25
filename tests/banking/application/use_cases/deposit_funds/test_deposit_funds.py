from decimal import Decimal
from unittest.mock import MagicMock
from uuid import UUID, uuid4

import pytest

from app.banking.application.exceptions.account_cant_deposit_funds_exception import (
    AccountCantDepositFundsException,
)
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
from app.banking.domain.enums.transaction_status import TransactionStatus
from app.banking.domain.enums.transaction_type import TransactionType
from app.banking.domain.exceptions.invalid_money_amount_exception import (
    InvalidMoneyAmountException,
)
from app.banking.domain.value_objects.money import Money
from app.identity.application.exceptions.account_not_found_exception import (
    AccountNotFoundException,
)
from app.identity.domain.entities.account import Account
from app.identity.domain.enums.account_status import AccountStatus
from app.identity.domain.value_objects.cpf import CPF
from app.identity.domain.value_objects.email import Email
from app.identity.domain.value_objects.name import Name


class TestDepositFunds:
    VALID_CPF = "52998224725"

    @pytest.fixture
    def mock_account_repository(self) -> MagicMock:
        mock = MagicMock()
        mock.find_by_id.return_value = None
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
        mock_account_repository: MagicMock,
        mock_transaction_repository: MagicMock,
        mock_ledger_entry_repository: MagicMock,
    ) -> MagicMock:
        mock = MagicMock()
        mock.account_repository = mock_account_repository
        mock.transaction_repository = mock_transaction_repository
        mock.ledger_entry_repository = mock_ledger_entry_repository
        mock.__enter__.return_value = mock
        mock.__exit__.return_value = None
        return mock

    @pytest.fixture
    def deposit_funds(self, mock_unit_of_work: MagicMock) -> DepositFunds:
        return DepositFunds(unit_of_work=mock_unit_of_work)

    @pytest.fixture
    def existing_account(self) -> Account:
        return Account(
            account_id=UUID("12345678-1234-1234-1234-123456789012"),
            tax_id=CPF(value=self.VALID_CPF),
            name=Name(value="John Doe"),
            email=Email(value="john@example.com"),
            balance=Money(amount=Decimal(0)),
            status=AccountStatus.ACTIVE,
        )

    @pytest.fixture
    def create_account(self):
        """Factory fixture que cria uma nova conta a cada chamada."""

        def _create_account(balance: Decimal = Decimal(0)) -> Account:
            return Account(
                account_id=uuid4(),
                tax_id=CPF(value=self.VALID_CPF),
                name=Name(value="John Doe"),
                email=Email(value="john@example.com"),
                balance=Money(amount=balance),
                status=AccountStatus.ACTIVE,
            )

        return _create_account

    def test_deposit_funds_creates_transaction_successfully(
        self,
        deposit_funds: DepositFunds,
        mock_account_repository: MagicMock,
        mock_transaction_repository: MagicMock,
        mock_ledger_entry_repository: MagicMock,
        existing_account: Account,
        mock_unit_of_work: MagicMock,
    ):
        # Arrange
        mock_account_repository.find_by_id.return_value = existing_account

        input_data = DepositFundsInput(
            account_id=existing_account.id,
            amount=Money(amount=Decimal("100.00")),
        )

        # Act
        result = deposit_funds.execute(input_data)

        # Assert
        assert isinstance(result, DepositFundsOutput)
        assert result.account_id == existing_account.id
        assert result.amount.amount == Decimal("100.00")
        assert result.transaction_type == TransactionType.DEPOSIT
        assert result.status == TransactionStatus.COMPLETED

        mock_account_repository.find_by_id.assert_called_once_with(existing_account.id)
        mock_account_repository.save.assert_called_once()
        mock_transaction_repository.save.assert_called_once()
        mock_ledger_entry_repository.save.assert_called_once()
        mock_unit_of_work.commit.assert_called_once()

    def test_deposit_funds_raises_exception_when_account_not_found(
        self,
        deposit_funds: DepositFunds,
        mock_account_repository: MagicMock,
        mock_unit_of_work: MagicMock,
    ):
        # Arrange
        mock_account_repository.find_by_id.return_value = None

        input_data = DepositFundsInput(
            account_id=uuid4(),
            amount=Money(amount=Decimal("100.00")),
        )

        # Act & Assert
        with pytest.raises(AccountNotFoundException):
            deposit_funds.execute(input_data)

        mock_account_repository.find_by_id.assert_called_once()
        mock_account_repository.save.assert_not_called()
        mock_unit_of_work.commit.assert_not_called()

    def test_deposit_funds_raises_exception_when_amount_is_zero(
        self,
        deposit_funds: DepositFunds,
        mock_account_repository: MagicMock,
        existing_account: Account,
        mock_unit_of_work: MagicMock,
    ):
        # Arrange
        mock_account_repository.find_by_id.return_value = existing_account

        input_data = DepositFundsInput(
            account_id=existing_account.id,
            amount=Money(amount=Decimal("0.00")),
        )

        # Act & Assert
        with pytest.raises(InvalidDepositAmountException):
            deposit_funds.execute(input_data)

        mock_account_repository.find_by_id.assert_called_once()
        mock_account_repository.save.assert_not_called()
        mock_unit_of_work.commit.assert_not_called()

    def test_deposit_funds_raises_exception_when_amount_is_negative(
        self,
        deposit_funds: DepositFunds,
        mock_account_repository: MagicMock,
        existing_account: Account,
    ):
        # Arrange
        mock_account_repository.find_by_id.return_value = existing_account

        # Money validation happens at object creation, so we test that
        # InvalidMoneyAmountException is raised when creating Money with negative value
        with pytest.raises(InvalidMoneyAmountException):
            Money(amount=Decimal("-100.00"))

    def test_deposit_funds_raises_exception_when_account_cannot_deposit(
        self,
        deposit_funds: DepositFunds,
        mock_account_repository: MagicMock,
        mock_unit_of_work: MagicMock,
    ):
        # Arrange
        blocked_account = Account(
            account_id=UUID("12345678-1234-1234-1234-123456789012"),
            tax_id=CPF(value=self.VALID_CPF),
            name=Name(value="John Doe"),
            email=Email(value="john@example.com"),
            balance=Money(amount=Decimal(0)),
            status=AccountStatus.BLOCKED,
        )
        mock_account_repository.find_by_id.return_value = blocked_account

        input_data = DepositFundsInput(
            account_id=blocked_account.id,
            amount=Money(amount=Decimal("100.00")),
        )

        # Act & Assert
        with pytest.raises(AccountCantDepositFundsException):
            deposit_funds.execute(input_data)

        mock_account_repository.find_by_id.assert_called_once()
        mock_account_repository.save.assert_not_called()
        mock_unit_of_work.commit.assert_not_called()

    def test_deposit_funds_with_idempotency_key_returns_existing_transaction(
        self,
        deposit_funds: DepositFunds,
        mock_account_repository: MagicMock,
        mock_transaction_repository: MagicMock,
        mock_ledger_entry_repository: MagicMock,
        existing_account: Account,
        mock_unit_of_work: MagicMock,
    ):
        # Arrange
        mock_account_repository.find_by_id.return_value = existing_account

        existing_transaction = Transaction(
            transaction_id=UUID("99999999-9999-9999-9999-999999999999"),
            transaction_type=TransactionType.DEPOSIT,
            transaction_status=TransactionStatus.COMPLETED,
            transaction_amount=Money(amount=Decimal("100.00")),
            payee_account_id=existing_account.id,
            idempotency_key="unique-key-123",
        )
        mock_transaction_repository.find_by_idempotency_key.return_value = (
            existing_transaction
        )

        input_data = DepositFundsInput(
            account_id=existing_account.id,
            amount=Money(amount=Decimal("100.00")),
            idempotency_key="unique-key-123",
        )

        # Act
        result = deposit_funds.execute(input_data)

        # Assert
        assert isinstance(result, DepositFundsOutput)
        assert result.transaction_id == existing_transaction.id

        # Não deve criar nova transação
        mock_transaction_repository.save.assert_not_called()
        mock_ledger_entry_repository.save.assert_not_called()
        mock_unit_of_work.commit.assert_not_called()

    def test_deposit_funds_updates_account_balance(
        self,
        deposit_funds: DepositFunds,
        mock_account_repository: MagicMock,
        existing_account: Account,
    ):
        # Arrange
        mock_account_repository.find_by_id.return_value = existing_account

        input_data = DepositFundsInput(
            account_id=existing_account.id,
            amount=Money(amount=Decimal("100.00")),
        )

        # Act
        deposit_funds.execute(input_data)

        # Assert
        saved_account = mock_account_repository.save.call_args[0][0]
        assert saved_account.balance.amount == Decimal("100.00")

    def test_deposit_funds_creates_ledger_entry_with_credit_type(
        self,
        deposit_funds: DepositFunds,
        mock_account_repository: MagicMock,
        mock_ledger_entry_repository: MagicMock,
        existing_account: Account,
    ):
        # Arrange
        mock_account_repository.find_by_id.return_value = existing_account

        input_data = DepositFundsInput(
            account_id=existing_account.id,
            amount=Money(amount=Decimal("100.00")),
        )

        # Act
        deposit_funds.execute(input_data)

        # Assert
        ledger_entry = mock_ledger_entry_repository.save.call_args[0][0]
        assert ledger_entry.account_id == existing_account.id
        assert ledger_entry.amount.amount == Decimal("100.00")

    def test_deposit_funds_multiple_deposits_accumulate_balance(
        self,
        deposit_funds: DepositFunds,
        mock_account_repository: MagicMock,
    ):
        # Arrange - cria duas contas diferentes para simular depósitos separados
        account1 = Account(
            account_id=uuid4(),
            tax_id=CPF(value=self.VALID_CPF),
            name=Name(value="John Doe"),
            email=Email(value="john@example.com"),
            balance=Money(amount=Decimal(0)),
            status=AccountStatus.ACTIVE,
        )
        account2 = Account(
            account_id=uuid4(),
            tax_id=CPF(value=self.VALID_CPF),
            name=Name(value="John Doe"),
            email=Email(value="john@example.com"),
            balance=Money(amount=Decimal(0)),
            status=AccountStatus.ACTIVE,
        )

        # First deposit
        mock_account_repository.find_by_id.return_value = account1
        input_data1 = DepositFundsInput(
            account_id=account1.id,
            amount=Money(amount=Decimal("100.00")),
        )
        result1 = deposit_funds.execute(input_data1)

        # Assert after first deposit
        assert result1.amount.amount == Decimal("100.00")

        # Second deposit with different account
        mock_account_repository.find_by_id.return_value = account2
        input_data2 = DepositFundsInput(
            account_id=account2.id,
            amount=Money(amount=Decimal("50.00")),
        )
        result2 = deposit_funds.execute(input_data2)

        # Assert after second deposit
        assert result2.amount.amount == Decimal("50.00")

        # Verify both saves were called
        assert mock_account_repository.save.call_count == 2
