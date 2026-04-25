from decimal import Decimal
from uuid import UUID

from uuid6 import uuid7

from app.banking.domain.value_objects.money import Money


class Wallet:
    def __init__(
        self,
        wallet_id: UUID,
        account_id: UUID,
        balance: Money,
    ) -> None:
        self._wallet_id = wallet_id
        self._account_id = account_id
        self._balance = balance

    @property
    def id(self) -> UUID:
        return self._wallet_id

    @property
    def account_id(self) -> UUID:
        return self._account_id

    @property
    def balance(self) -> Money:
        return self._balance

    @property
    def currency(self) -> str:
        return self._balance.currency

    def deposit(self, amount: Money) -> None:
        self._balance = self._balance.add(amount)

    @classmethod
    def create(
        cls,
        account_id: UUID,
        currency: str = "BRL",
    ) -> "Wallet":
        return cls(
            wallet_id=uuid7(),
            account_id=account_id,
            balance=Money(amount=Decimal("0.00"), currency=currency),
        )

    @classmethod
    def restore(
        cls,
        wallet_id: UUID,
        account_id: UUID,
        balance: Money,
    ) -> "Wallet":
        return cls(
            wallet_id=wallet_id,
            account_id=account_id,
            balance=balance,
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Wallet):
            return False
        return self._wallet_id == other._wallet_id

    def __hash__(self) -> int:
        return hash(self._wallet_id)
