from decimal import Decimal

import pytest

from app.banking.domain.exceptions.currency_mismatch_exception import (
    CurrencyMismatchException,
)
from app.banking.domain.exceptions.insufficient_funds_exception import (
    InsufficientFundsException,
)
from app.banking.domain.exceptions.invalid_money_amount_exception import (
    InvalidMoneyAmountException,
)
from app.banking.domain.value_objects.money import Money


class TestMoney:
    def test_create_money_with_valid_amount(self):
        money = Money(amount=Decimal("100.00"))
        assert money.amount == Decimal("100.00")
        assert money.currency == "BRL"

    def test_create_money_with_default_currency(self):
        money = Money(amount=Decimal("50.00"))
        assert money.currency == "BRL"

    def test_create_money_with_custom_currency(self):
        money = Money(amount=Decimal("100.00"), currency="USD")
        assert money.currency == "USD"

    def test_money_normalizes_decimal_places(self):
        money = Money(amount=Decimal("100.123"))
        assert money.amount == Decimal("100.12")

    def test_money_rounds_half_up(self):
        money = Money(amount=Decimal("100.125"))
        assert money.amount == Decimal("100.13")

    def test_money_zero_is_valid(self):
        money = Money(amount=Decimal("0.00"))
        assert money.amount == Decimal("0.00")

    def test_money_negative_amount_raises_exception(self):
        with pytest.raises(InvalidMoneyAmountException):
            Money(amount=Decimal("-100.00"))

    def test_money_is_zero(self):
        money = Money(amount=Decimal("0.00"))
        assert money.is_zero() is True

    def test_money_is_zero_false(self):
        money = Money(amount=Decimal("100.00"))
        assert money.is_zero() is False

    def test_money_is_positive(self):
        money = Money(amount=Decimal("100.00"))
        assert money.is_positive() is True

    def test_money_is_positive_false(self):
        money = Money(amount=Decimal("0.00"))
        assert money.is_positive() is False

    # --- Testes para add ---

    def test_money_add_two_money_values(self):
        money1 = Money(amount=Decimal("100.00"))
        money2 = Money(amount=Decimal("50.00"))

        result = money1.add(money2)

        assert result.amount == Decimal("150.00")
        assert result.currency == "BRL"

    def test_money_add_different_currencies_raises_exception(self):
        money1 = Money(amount=Decimal("100.00"), currency="BRL")
        money2 = Money(amount=Decimal("50.00"), currency="USD")

        with pytest.raises(CurrencyMismatchException):
            money1.add(money2)

    # --- Testes para subtract ---

    def test_money_subtract_two_money_values(self):
        money1 = Money(amount=Decimal("100.00"))
        money2 = Money(amount=Decimal("50.00"))

        result = money1.subtract(money2)

        assert result.amount == Decimal("50.00")
        assert result.currency == "BRL"

    def test_money_subtract_insufficient_funds_raises_exception(self):
        money1 = Money(amount=Decimal("50.00"))
        money2 = Money(amount=Decimal("100.00"))

        with pytest.raises(InsufficientFundsException):
            money1.subtract(money2)

    def test_money_subtract_different_currencies_raises_exception(self):
        money1 = Money(amount=Decimal("100.00"), currency="BRL")
        money2 = Money(amount=Decimal("50.00"), currency="USD")

        with pytest.raises(CurrencyMismatchException):
            money1.subtract(money2)

    # --- Testes para greater_than ---

    def test_money_greater_than_true(self):
        money1 = Money(amount=Decimal("100.00"))
        money2 = Money(amount=Decimal("50.00"))

        assert money1.greater_than(money2) is True

    def test_money_greater_than_false(self):
        money1 = Money(amount=Decimal("50.00"))
        money2 = Money(amount=Decimal("100.00"))

        assert money1.greater_than(money2) is False

    def test_money_greater_than_equal_returns_false(self):
        money1 = Money(amount=Decimal("100.00"))
        money2 = Money(amount=Decimal("100.00"))

        assert money1.greater_than(money2) is False

    def test_money_greater_than_different_currencies_raises_exception(self):
        money1 = Money(amount=Decimal("100.00"), currency="BRL")
        money2 = Money(amount=Decimal("50.00"), currency="USD")

        with pytest.raises(CurrencyMismatchException):
            money1.greater_than(money2)

    # --- Testes para less_than ---

    def test_money_less_than_true(self):
        money1 = Money(amount=Decimal("50.00"))
        money2 = Money(amount=Decimal("100.00"))

        assert money1.less_than(money2) is True

    def test_money_less_than_false(self):
        money1 = Money(amount=Decimal("100.00"))
        money2 = Money(amount=Decimal("50.00"))

        assert money1.less_than(money2) is False

    def test_money_less_than_equal_returns_false(self):
        money1 = Money(amount=Decimal("100.00"))
        money2 = Money(amount=Decimal("100.00"))

        assert money1.less_than(money2) is False

    def test_money_less_than_different_currencies_raises_exception(self):
        money1 = Money(amount=Decimal("50.00"), currency="BRL")
        money2 = Money(amount=Decimal("100.00"), currency="USD")

        with pytest.raises(CurrencyMismatchException):
            money1.less_than(money2)

    # --- Testes de imutabilidade ---

    def test_money_add_returns_new_instance(self):
        money1 = Money(amount=Decimal("100.00"))
        money2 = Money(amount=Decimal("50.00"))

        result = money1.add(money2)

        # Original should not be modified
        assert money1.amount == Decimal("100.00")
        assert result.amount == Decimal("150.00")
        # Should be different instances
        assert result is not money1

    def test_money_subtract_returns_new_instance(self):
        money1 = Money(amount=Decimal("100.00"))
        money2 = Money(amount=Decimal("50.00"))

        result = money1.subtract(money2)

        # Original should not be modified
        assert money1.amount == Decimal("100.00")
        assert result.amount == Decimal("50.00")
        # Should be different instances
        assert result is not money1

    # --- Testes para __eq__ e __hash__ ---

    def test_money_equality_same_amount_and_currency(self):
        money1 = Money(amount=Decimal("100.00"))
        money2 = Money(amount=Decimal("100.00"))

        assert money1 == money2

    def test_money_equality_different_amount(self):
        money1 = Money(amount=Decimal("100.00"))
        money2 = Money(amount=Decimal("50.00"))

        assert money1 != money2

    def test_money_equality_different_currency(self):
        money1 = Money(amount=Decimal("100.00"), currency="BRL")
        money2 = Money(amount=Decimal("100.00"), currency="USD")

        assert money1 != money2

    def test_money_equality_different_type(self):
        money = Money(amount=Decimal("100.00"))

        assert money != "not money"

    def test_money_hash_same_amount_and_currency(self):
        money1 = Money(amount=Decimal("100.00"))
        money2 = Money(amount=Decimal("100.00"))

        assert hash(money1) == hash(money2)

    def test_money_can_be_used_in_set(self):
        money1 = Money(amount=Decimal("100.00"))
        money2 = Money(amount=Decimal("100.00"))
        money3 = Money(amount=Decimal("50.00"))

        money_set = {money1, money2, money3}

        # money1 and money2 are equal, so only 2 should be in the set
        assert len(money_set) == 2

    def test_money_can_be_used_as_dict_key(self):
        money = Money(amount=Decimal("100.00"))

        money_dict = {money: "test value"}

        assert money_dict[money] == "test value"
