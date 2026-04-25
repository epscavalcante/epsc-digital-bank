from decimal import Decimal
from uuid import UUID

from uuid6 import uuid7

from app.banking.domain.value_objects.money import Money
from app.identity.domain.enums.account_status import AccountStatus
from app.identity.domain.value_objects.cpf import CPF
from app.identity.domain.value_objects.email import Email
from app.identity.domain.value_objects.name import Name


class Account:
    def __init__(
        self,
        account_id: UUID,
        tax_id: CPF,
        name: Name,
        email: Email,
        balance: Money,
        status: AccountStatus = AccountStatus.ACTIVE,
    ) -> None:
        self._account_id = account_id
        self._name = name
        self._tax_id = tax_id
        self._email = email
        self._status = status
        self._balance = balance

    # --- Propriedades (Getters) ---

    @property
    def id(self) -> UUID:
        # Se o teste pede 'id', mapeamos o _account_id para cá
        return self._account_id

    @property
    def account_id(self) -> UUID:
        return self._account_id

    @property
    def name(self) -> Name:
        return self._name

    @property
    def email(self) -> Email:
        return self._email

    @property
    def tax_id(self) -> CPF:
        return self._tax_id

    def can_deposit_funds(self) -> bool:
        return self._status == AccountStatus.ACTIVE

    def can_receive_funds(self) -> bool:
        return self._status in [
            AccountStatus.ACTIVE,
            AccountStatus.BLOCKED,
        ]

    def can_transfer_funds(self) -> bool:
        return self._status == AccountStatus.ACTIVE

    def deposit(self, amount: Money) -> None:
        self._balance = self._balance.add(amount)

    @property
    def balance(self) -> Money:
        return self._balance

    # --- Métodos de Fábrica ---

    @classmethod
    def create(
        cls,
        name: str,
        email: str,
        tax_id: str,
    ) -> "Account":
        return cls(
            account_id=uuid7(),
            tax_id=CPF(value=tax_id),
            name=Name(value=name),
            email=Email(value=email),
            balance=Money(amount=Decimal(0)),
        )

    @classmethod
    def restore(
        cls,
        account_id: UUID,
        name: str,
        email: str,
        tax_id: str,
    ) -> "Account":
        return cls(
            account_id=account_id,
            tax_id=CPF(value=tax_id),
            name=Name(value=name),
            email=Email(value=email),
            balance=Money(amount=Decimal(0)),
        )

    @property
    def status(self) -> AccountStatus:
        return self._status

    def __eq__(self, other: object) -> bool:
        # No DDD, entidades são iguais se seus IDs forem iguais
        if not isinstance(other, Account):
            return False
        return self._account_id == other._account_id

    def __hash__(self) -> int:
        return hash(self._account_id)
