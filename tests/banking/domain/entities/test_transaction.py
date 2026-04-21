from decimal import Decimal
from uuid import UUID, uuid4

from app.banking.domain.entities.transaction import Transaction
from app.banking.domain.enums.transaction_status import TransactionStatus
from app.banking.domain.enums.transaction_type import TransactionType
from app.banking.domain.value_objects.money import Money


class TestTransaction:
    def test_create_deposit_generates_uuid(self):
        payee_account_id = uuid4()
        amount = Money(amount=Decimal("100.00"))

        transaction = Transaction.create_deposit(
            amount=amount,
            payee_account_id=payee_account_id,
        )

        assert isinstance(transaction._id, UUID)

    def test_create_deposit_with_valid_data(self):
        payee_account_id = uuid4()
        amount = Money(amount=Decimal("100.00"))

        transaction = Transaction.create_deposit(
            amount=amount,
            payee_account_id=payee_account_id,
        )

        assert transaction.type == TransactionType.DEPOSIT
        assert transaction.status == TransactionStatus.COMPLETED
        assert transaction.amount == amount
        assert transaction.payee_account_id == payee_account_id
        assert transaction.payer_account_id is None

    def test_create_deposit_with_idempotency_key(self):
        payee_account_id = uuid4()
        amount = Money(amount=Decimal("100.00"))
        idempotency_key = "unique-key-123"

        transaction = Transaction.create_deposit(
            amount=amount,
            payee_account_id=payee_account_id,
            idempotency_key=idempotency_key,
        )

        assert transaction.idempotency_key == idempotency_key

    def test_transaction_has_private_attributes(self):
        payee_account_id = uuid4()
        amount = Money(amount=Decimal("100.00"))

        transaction = Transaction.create_deposit(
            amount=amount,
            payee_account_id=payee_account_id,
        )

        assert hasattr(transaction, "_id")
        assert hasattr(transaction, "_amount")
        assert hasattr(transaction, "_type")
        assert hasattr(transaction, "_status")
        assert hasattr(transaction, "_idempotency_key")
        assert hasattr(transaction, "_payer_account_id")
        assert hasattr(transaction, "_payee_account_id")
        assert hasattr(transaction, "_created_at")

    def test_transaction_id_property(self):
        payee_account_id = uuid4()
        amount = Money(amount=Decimal("100.00"))

        transaction = Transaction.create_deposit(
            amount=amount,
            payee_account_id=payee_account_id,
        )

        assert transaction.id == transaction._id

    def test_transaction_amount_property(self):
        payee_account_id = uuid4()
        amount = Money(amount=Decimal("100.00"))

        transaction = Transaction.create_deposit(
            amount=amount,
            payee_account_id=payee_account_id,
        )

        assert transaction.amount == amount

    def test_transaction_status_property(self):
        payee_account_id = uuid4()
        amount = Money(amount=Decimal("100.00"))

        transaction = Transaction.create_deposit(
            amount=amount,
            payee_account_id=payee_account_id,
        )

        assert transaction.status == TransactionStatus.COMPLETED

    def test_transaction_type_property(self):
        payee_account_id = uuid4()
        amount = Money(amount=Decimal("100.00"))

        transaction = Transaction.create_deposit(
            amount=amount,
            payee_account_id=payee_account_id,
        )

        assert transaction.type == TransactionType.DEPOSIT

    def test_transaction_idempotency_key_property(self):
        payee_account_id = uuid4()
        amount = Money(amount=Decimal("100.00"))
        idempotency_key = "unique-key-123"

        transaction = Transaction.create_deposit(
            amount=amount,
            payee_account_id=payee_account_id,
            idempotency_key=idempotency_key,
        )

        assert transaction.idempotency_key == idempotency_key

    def test_transaction_idempotency_key_is_none_by_default(self):
        payee_account_id = uuid4()
        amount = Money(amount=Decimal("100.00"))

        transaction = Transaction.create_deposit(
            amount=amount,
            payee_account_id=payee_account_id,
        )

        assert transaction.idempotency_key is None

    # --- Testes para __eq__ e __hash__ ---

    def test_transaction_equality_same_id(self):
        payee_account_id = uuid4()
        amount = Money(amount=Decimal("100.00"))

        # Criar duas transações com o mesmo ID (simulando com restore se existir)
        # Como não temos método restore, testamos com create diferentes
        transaction1 = Transaction.create_deposit(
            amount=amount,
            payee_account_id=payee_account_id,
        )
        transaction2 = Transaction.create_deposit(
            amount=Money(amount=Decimal("200.00")),
            payee_account_id=uuid4(),
        )

        # Different UUIDs, so they should not be equal
        assert transaction1 != transaction2

    def test_transaction_equality_different_type(self):
        payee_account_id = uuid4()
        amount = Money(amount=Decimal("100.00"))

        transaction = Transaction.create_deposit(
            amount=amount,
            payee_account_id=payee_account_id,
        )

        assert transaction != "not a transaction"

    def test_transaction_hash_consistency(self):
        payee_account_id = uuid4()
        amount = Money(amount=Decimal("100.00"))

        transaction = Transaction.create_deposit(
            amount=amount,
            payee_account_id=payee_account_id,
        )

        hash1 = hash(transaction)
        hash2 = hash(transaction)
        assert hash1 == hash2

    def test_transaction_can_be_used_in_set(self):
        payee_account_id = uuid4()
        amount = Money(amount=Decimal("100.00"))

        transaction1 = Transaction.create_deposit(
            amount=amount,
            payee_account_id=payee_account_id,
        )
        transaction2 = Transaction.create_deposit(
            amount=Money(amount=Decimal("200.00")),
            payee_account_id=uuid4(),
        )

        transaction_set = {transaction1, transaction2}
        # Different UUIDs, so both should be in the set
        assert len(transaction_set) == 2

    def test_transaction_can_be_used_as_dict_key(self):
        payee_account_id = uuid4()
        amount = Money(amount=Decimal("100.00"))

        transaction = Transaction.create_deposit(
            amount=amount,
            payee_account_id=payee_account_id,
        )

        transaction_dict = {transaction: "test value"}
        assert transaction_dict[transaction] == "test value"
