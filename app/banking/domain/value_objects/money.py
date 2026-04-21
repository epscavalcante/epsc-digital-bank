from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

from app.banking.domain.exceptions.currency_mismatch_exception import (
    CurrencyMismatchException,
)
from app.banking.domain.exceptions.insufficient_funds_exception import (
    InsufficientFundsException,
)
from app.banking.domain.exceptions.invalid_money_amount_exception import (
    InvalidMoneyAmountException,
)


@dataclass(frozen=True, slots=True)
class Money:
    amount: Decimal
    currency: str = "BRL"

    def __post_init__(self) -> None:
        normalized_amount = self.amount.quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )

        if normalized_amount < Decimal("0.00"):
            raise InvalidMoneyAmountException()

        object.__setattr__(self, "amount", normalized_amount)

    def is_zero(self) -> bool:
        return self.amount == Decimal("0.00")

    def is_positive(self) -> bool:
        return self.amount > Decimal("0.00")

    def add(self, other: "Money") -> "Money":
        self._ensure_same_currency(other)

        return Money(
            amount=self.amount + other.amount,
            currency=self.currency,
        )

    def subtract(self, other: "Money") -> "Money":
        self._ensure_same_currency(other)

        result = self.amount - other.amount

        if result < Decimal("0.00"):
            raise InsufficientFundsException()

        return Money(
            amount=result,
            currency=self.currency,
        )

    def greater_than(self, other: "Money") -> bool:
        self._ensure_same_currency(other)

        return self.amount > other.amount

    def less_than(self, other: "Money") -> bool:
        self._ensure_same_currency(other)

        return self.amount < other.amount

    def _ensure_same_currency(self, other: "Money") -> None:
        if self.currency != other.currency:
            raise CurrencyMismatchException()
