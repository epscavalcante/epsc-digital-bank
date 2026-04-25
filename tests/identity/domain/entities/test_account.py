from uuid import UUID

from app.identity.domain.entities.account import Account
from app.identity.domain.enums.account_status import AccountStatus
from app.identity.domain.value_objects.cpf import CPF
from app.identity.domain.value_objects.email import Email
from app.identity.domain.value_objects.name import Name


class TestAccount:
    VALID_CPF = "52998224725"
    VALID_CPF_2 = "11144477735"

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

    # --- Testes para propriedade id ---

    def test_account_id_property_alias(self):
        existing_uuid = UUID("12345678-1234-1234-1234-123456789012")
        account = Account.restore(
            account_id=existing_uuid,
            name="John Doe",
            email="john@example.com",
            tax_id=self.VALID_CPF,
        )
        assert account.id == existing_uuid
        assert account.id == account.account_id

    # --- Testes para status ---

    def test_account_status_default_is_active(self):
        account = Account.create(
            name="John Doe",
            email="john@example.com",
            tax_id=self.VALID_CPF,
        )
        assert account.status == AccountStatus.ACTIVE

    # --- Testes para __eq__ e __hash__ ---

    def test_account_equality_same_id(self):
        existing_uuid = UUID("12345678-1234-1234-1234-123456789012")
        account1 = Account.restore(
            account_id=existing_uuid,
            name="John Doe",
            email="john@example.com",
            tax_id=self.VALID_CPF,
        )
        account2 = Account.restore(
            account_id=existing_uuid,
            name="Jane Doe",
            email="jane@example.com",
            tax_id=self.VALID_CPF_2,
        )
        assert account1 == account2

    def test_account_equality_different_id(self):
        account1 = Account.create(
            name="John Doe",
            email="john@example.com",
            tax_id=self.VALID_CPF,
        )
        account2 = Account.create(
            name="John Doe",
            email="john@example.com",
            tax_id=self.VALID_CPF_2,
        )
        # Different UUIDs, so they should not be equal
        assert account1 != account2

    def test_account_equality_different_type(self):
        account = Account.create(
            name="John Doe",
            email="john@example.com",
            tax_id=self.VALID_CPF,
        )
        assert account != "not an account"

    def test_account_hash_same_id(self):
        existing_uuid = UUID("12345678-1234-1234-1234-123456789012")
        account1 = Account.restore(
            account_id=existing_uuid,
            name="John Doe",
            email="john@example.com",
            tax_id=self.VALID_CPF,
        )
        account2 = Account.restore(
            account_id=existing_uuid,
            name="Jane Doe",
            email="jane@example.com",
            tax_id=self.VALID_CPF_2,
        )
        assert hash(account1) == hash(account2)

    def test_account_can_be_used_in_set(self):
        existing_uuid = UUID("12345678-1234-1234-1234-123456789012")
        account1 = Account.restore(
            account_id=existing_uuid,
            name="John Doe",
            email="john@example.com",
            tax_id=self.VALID_CPF,
        )
        account2 = Account.restore(
            account_id=existing_uuid,
            name="Jane Doe",
            email="jane@example.com",
            tax_id=self.VALID_CPF_2,
        )
        account_set = {account1, account2}
        # Same ID means only one account in the set
        assert len(account_set) == 1

    def test_account_can_be_used_as_dict_key(self):
        existing_uuid = UUID("12345678-1234-1234-1234-123456789012")
        account = Account.restore(
            account_id=existing_uuid,
            name="John Doe",
            email="john@example.com",
            tax_id=self.VALID_CPF,
        )
        account_dict = {account: "test value"}
        assert account_dict[account] == "test value"
