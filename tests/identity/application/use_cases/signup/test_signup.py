from decimal import Decimal
from unittest.mock import MagicMock
from uuid import UUID

from app.banking.domain.value_objects.money import Money
import pytest

from app.identity.application.exceptions.account_already_exists_exception import (
    AccountAlreadyExistsException,
)
from app.identity.application.use_cases.signup.signup import Signup
from app.identity.application.use_cases.signup.signup_input import SignupInput
from app.identity.application.use_cases.signup.signup_output import SignupOutput
from app.identity.domain.entities.account import Account
from app.identity.domain.value_objects.cpf import CPF
from app.identity.domain.value_objects.email import Email
from app.identity.domain.value_objects.name import Name


class TestSignup:
    VALID_CPF = "52998224725"  # CPF válido real

    @pytest.fixture
    def mock_account_repository(self) -> MagicMock:
        mock = MagicMock()
        # Configurar o mock para aceitar qualquer chamada de método
        mock.find_by_tax_id.return_value = None
        mock.find_by_email.return_value = None
        mock.create.return_value = None
        return mock

    @pytest.fixture
    def signup(self, mock_account_repository: MagicMock) -> Signup:
        return Signup(account_repository=mock_account_repository)

    def test_signup_creates_account_successfully(
        self, signup: Signup, mock_account_repository: MagicMock
    ):
        # Arrange
        mock_account_repository.find_by_tax_id.return_value = None
        mock_account_repository.find_by_email.return_value = None

        input_data = SignupInput(
            tax_id=self.VALID_CPF,
            name="John Doe",
            email="john@example.com",
        )

        # Act
        result = signup.execute(input_data)

        # Assert
        assert isinstance(result, SignupOutput)
        assert result.account_id is not None
        mock_account_repository.find_by_tax_id.assert_called_once()
        mock_account_repository.find_by_email.assert_called_once()
        mock_account_repository.save.assert_called_once()

    def test_signup_raises_exception_when_cpf_already_exists(
        self, signup: Signup, mock_account_repository: MagicMock
    ):
        # Arrange
        existing_account = Account(
            account_id=UUID("12345678-1234-1234-1234-123456789012"),
            tax_id=CPF(value=self.VALID_CPF),
            name=Name(value="Existing User"),
            email=Email(value="existing@example.com"),
            balance=Money(amount=Decimal(0)),
        )
        mock_account_repository.find_by_tax_id.return_value = existing_account

        input_data = SignupInput(
            tax_id=self.VALID_CPF,
            name="John Doe",
            email="john@example.com",
        )

        # Act & Assert
        with pytest.raises(AccountAlreadyExistsException):
            signup.execute(input_data)

        mock_account_repository.find_by_tax_id.assert_called_once()
        mock_account_repository.find_by_email.assert_not_called()
        mock_account_repository.create.assert_not_called()

    def test_signup_raises_exception_when_email_already_exists(
        self, signup: Signup, mock_account_repository: MagicMock
    ):
        # Arrange
        mock_account_repository.find_by_tax_id.return_value = None

        existing_account = Account(
            account_id=UUID("12345678-1234-1234-1234-123456789012"),
            tax_id=CPF(value=self.VALID_CPF),
            name=Name(value="Existing User"),
            email=Email(value="john@example.com"),
            balance=Money(amount=Decimal(0)),
        )
        mock_account_repository.find_by_email.return_value = existing_account

        input_data = SignupInput(
            tax_id=self.VALID_CPF,
            name="John Doe",
            email="john@example.com",
        )

        # Act & Assert
        with pytest.raises(AccountAlreadyExistsException):
            signup.execute(input_data)

        mock_account_repository.find_by_tax_id.assert_called_once()
        mock_account_repository.find_by_email.assert_called_once()
        mock_account_repository.create.assert_not_called()

    def test_signup_calls_repository_with_normalized_values(
        self, signup: Signup, mock_account_repository: MagicMock
    ):
        # Arrange
        mock_account_repository.find_by_tax_id.return_value = None
        mock_account_repository.find_by_email.return_value = None

        created_account = Account(
            account_id=UUID("12345678-1234-1234-1234-123456789012"),
            tax_id=CPF(value=self.VALID_CPF),
            name=Name(value="John Doe"),
            email=Email(value="john@example.com"),
            balance=Money(amount=Decimal(0)),
        )
        mock_account_repository.create.return_value = created_account

        input_data = SignupInput(
            tax_id="529.982.247-25",  # Com formatação
            name="  John Doe  ",  # Com espaços
            email="JOHN@EXAMPLE.COM",  # Maiúsculas
        )

        # Act
        result = signup.execute(input_data)

        # Assert
        assert isinstance(result, SignupOutput)
        # Verifica que o CPF foi normalizado (apenas dígitos)
        call_args = mock_account_repository.find_by_tax_id.call_args
        assert call_args[0][0].value == "52998224725"
        # Verifica que o email foi normalizado (lowercase)
        call_args = mock_account_repository.find_by_email.call_args
        assert call_args[0][0].value == "john@example.com"
