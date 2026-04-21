from uuid import UUID


from app.identity.domain.entities.account import Account
from app.identity.domain.value_objects.cpf import CPF
from app.identity.domain.value_objects.email import Email
from app.identity.domain.value_objects.name import Name


class TestAccount:
    VALID_CPF = "52998224725"

    def test_create_account_generates_uuid(self):
        account = Account.create(
            name="John Doe",
            email="john@example.com",
            tax_id=self.VALID_CPF,
        )
        assert isinstance(account._account_id, UUID)

    def test_create_account_with_valid_data(self):
        account = Account.create(
            name="John Doe",
            email="john@example.com",
            tax_id=self.VALID_CPF,
        )
        assert account.name.value == "John Doe"
        assert account.email.value == "john@example.com"
        assert account.tax_id.value == self.VALID_CPF

    def test_restore_account_with_existing_uuid(self):
        existing_uuid = UUID("12345678-1234-1234-1234-123456789012")
        account = Account.restore(
            account_id=existing_uuid,
            name="John Doe",
            email="john@example.com",
            tax_id=self.VALID_CPF,
        )
        assert account._account_id == existing_uuid

    def test_account_has_private_attributes(self):
        account = Account.create(
            name="John Doe",
            email="john@example.com",
            tax_id=self.VALID_CPF,
        )
        # Verifica que os atributos são privados
        assert hasattr(account, "_account_id")
        assert hasattr(account, "_name")
        assert hasattr(account, "_tax_id")
        assert hasattr(account, "_email")

    def test_account_id_property(self):
        existing_uuid = UUID("12345678-1234-1234-1234-123456789012")
        account = Account.restore(
            account_id=existing_uuid,
            name="John Doe",
            email="john@example.com",
            tax_id=self.VALID_CPF,
        )
        assert account._account_id == existing_uuid

    def test_account_name_property(self):
        account = Account.create(
            name="John Doe",
            email="john@example.com",
            tax_id=self.VALID_CPF,
        )
        assert account.name == Name(value="John Doe")

    def test_account_email_property(self):
        account = Account.create(
            name="John Doe",
            email="john@example.com",
            tax_id=self.VALID_CPF,
        )
        assert account.email == Email(value="john@example.com")

    def test_account_tax_id_property(self):
        account = Account.create(
            name="John Doe",
            email="john@example.com",
            tax_id=self.VALID_CPF,
        )
        assert account.tax_id == CPF(value=self.VALID_CPF)

    def test_create_account_normalizes_email(self):
        account = Account.create(
            name="John Doe",
            email="JOHN@EXAMPLE.COM",
            tax_id=self.VALID_CPF,
        )
        assert account.email.value == "john@example.com"

    def test_create_account_normalizes_cpf(self):
        account = Account.create(
            name="John Doe",
            email="john@example.com",
            tax_id="529.982.247-25",
        )
        assert account.tax_id.value == self.VALID_CPF

    def test_create_account_strips_name(self):
        account = Account.create(
            name="  John Doe  ",
            email="john@example.com",
            tax_id=self.VALID_CPF,
        )
        assert account.name.value == "John Doe"
