from datetime import UTC, datetime
from uuid import UUID

from uuid6 import uuid7

from app.banking.domain.enums.transaction_status import TransactionStatus
from app.banking.domain.enums.transaction_type import TransactionType
from app.banking.domain.value_objects.money import Money


class Transaction:
    def __init__(
        self,
        transaction_id: UUID,
        transaction_type: TransactionType,
        transaction_status: TransactionStatus,
        transaction_amount: Money,
        idempotency_key: str | None = None,
        payer_account_id: UUID | None = None,
        payee_account_id: UUID | None = None,
        created_at: datetime | None = None,
    ) -> None:
        self._id = transaction_id
        self._amount = transaction_amount
        self._type = transaction_type
        self._status = transaction_status
        self._idempotency_key = idempotency_key
        self._payer_account_id = payer_account_id
        self._payee_account_id = payee_account_id
        self._created_at = created_at

    # --- Propriedades (Getters) ---
    @property
    def id(self) -> UUID:
        return self._id

    @property
    def amount(self) -> Money:
        return self._amount

    @property
    def status(self) -> TransactionStatus:
        return self._status

    @property
    def type(self) -> TransactionType:
        return self._type

    @property
    def idempotency_key(self) -> str | None:
        return self._idempotency_key

    @property
    def payer_account_id(self) -> UUID | None:
        return self._payer_account_id

    @property
    def payee_account_id(self) -> UUID | None:
        return self._payee_account_id

    @property
    def created_at(self) -> datetime | None:
        return self._created_at

    # --- Métodos de Fábrica ---
    @classmethod
    def create_deposit(
        cls,
        amount: Money,
        payee_account_id: UUID,
        idempotency_key: str | None = None,
    ) -> "Transaction":
        return cls(
            transaction_id=uuid7(),
            transaction_type=TransactionType.DEPOSIT,
            transaction_status=TransactionStatus.COMPLETED,
            transaction_amount=amount,
            payer_account_id=None,
            payee_account_id=payee_account_id,
            idempotency_key=idempotency_key,
            created_at=datetime.now(UTC),
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Transaction):
            return False
        return self._id == other._id

    def __hash__(self) -> int:
        return hash(self._id)
