from uuid import UUID

import pytest

from app.identity.application.exceptions.account_already_exists_exception import (
    AccountAlreadyExistsException,
)
from app.identity.application.use_cases.signup.signup import Signup
from app.identity.application.use_cases.signup.signup_input import SignupInput
from app.identity.application.use_cases.signup.signup_output import SignupOutput
from app.identity.domain.entities.account import Account
from app.identity.domain.enums.account_status import AccountStatus
from app.identity.infrastructure.database import Database
from app.shared.infrastructure.sqlalchemy_unit_of_work import SqlAlchemyUnitOfWork


class TestSignupIntegration:
    """Testes de integração do Signup usando SQLite."""

    VALID_CPF = "52998224725"

    @pytest.fixture
    def database(self, tmp_path):
        """Cria um banco de dados SQLite temporário e garante fechamento do engine."""
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
    def signup(self, unit_of_work):
        """Cria o use case Signup com o repository real."""
        return Signup(unit_of_work=unit_of_work)

    def test_signup_creates_account_in_database(self, signup, unit_of_work):
        """Testa que o signup cria a conta corretamente no banco de dados."""
        # Arrange
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
        assert isinstance(result.account_id, UUID)

        # Verifica que a conta foi persistida no banco
        with unit_of_work as verify_uow:
            saved_account = verify_uow.account_repository.find_by_id(result.account_id)
            saved_wallet = verify_uow.wallet_repository.find_by_account_id(
                result.account_id
            )
        assert saved_account is not None
        assert saved_wallet is not None
        assert saved_account.name.value == "John Doe"
        assert saved_account.email.value == "john@example.com"
        assert saved_account.tax_id.value == self.VALID_CPF
        assert saved_account.status == AccountStatus.ACTIVE
        assert saved_wallet.balance.currency == "BRL"

    def test_signup_finds_existing_account_by_tax_id(self, signup, unit_of_work):
        """Testa que o signup encontra conta existente pelo CPF."""
        # Arrange - cria uma conta primeiro
        existing_account = Account.restore(
            account_id=UUID("12345678-1234-1234-1234-123456789012"),
            tax_id=self.VALID_CPF,
            name="Existing User",
            email="existing@example.com",
        )
        with unit_of_work as setup_uow:
            setup_uow.account_repository.save(existing_account)
            setup_uow.commit()

        input_data = SignupInput(
            tax_id=self.VALID_CPF,
            name="John Doe",
            email="john2@example.com",
        )

        # Act & Assert - deve falhar porque o CPF já existe
        with pytest.raises(AccountAlreadyExistsException):
            signup.execute(input_data)

    def test_signup_finds_existing_account_by_email(self, signup, unit_of_work):
        """Testa que o signup encontra conta existente pelo email."""
        # Arrange - cria uma conta primeiro
        existing_account = Account.restore(
            account_id=UUID("12345678-1234-1234-1234-123456789012"),
            tax_id="11144477735",
            name="Existing User",
            email="john@example.com",
        )
        with unit_of_work as setup_uow:
            setup_uow.account_repository.save(existing_account)
            setup_uow.commit()

        input_data = SignupInput(
            tax_id=self.VALID_CPF,
            name="John Doe",
            email="john@example.com",
        )

        # Act & Assert - deve falhar porque o email já existe
        with pytest.raises(AccountAlreadyExistsException):
            signup.execute(input_data)

    def test_signup_normalizes_values_before_saving(self, signup, unit_of_work):
        """Testa que o signup normaliza CPF, email e nome antes de salvar."""
        # Arrange
        input_data = SignupInput(
            tax_id="529.982.247-25",  # Com formatação
            name="  John Doe  ",  # Com espaços
            email="JOHN@EXAMPLE.COM",  # Maiúsculas
        )

        # Act
        result = signup.execute(input_data)

        # Assert - verifica que os valores foram normalizados no banco
        with unit_of_work as verify_uow:
            saved_account = verify_uow.account_repository.find_by_id(result.account_id)
        assert saved_account is not None
        assert saved_account.tax_id.value == "52998224725"  # Sem formatação
        assert saved_account.email.value == "john@example.com"  # Lowercase
        assert saved_account.name.value == "John Doe"  # Sem espaços

    def test_signup_creates_wallet_with_zero_balance(self, signup, unit_of_work):
        """Testa que a wallet inicial é criada com saldo zero."""
        # Arrange
        input_data = SignupInput(
            tax_id=self.VALID_CPF,
            name="John Doe",
            email="john@example.com",
        )

        # Act
        result = signup.execute(input_data)

        # Assert
        with unit_of_work as verify_uow:
            saved_wallet = verify_uow.wallet_repository.find_by_account_id(
                result.account_id
            )
        assert saved_wallet is not None
        assert saved_wallet.balance.amount == 0
        assert saved_wallet.balance.currency == "BRL"
