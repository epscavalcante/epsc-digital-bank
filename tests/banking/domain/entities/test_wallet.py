from decimal import Decimal
from uuid import UUID

from app.banking.domain.entities.wallet import Wallet
from app.banking.domain.value_objects.money import Money


class TestWallet:
    def test_create_wallet_starts_with_zero_balance_in_brl(self):
        wallet = Wallet.create(
            account_id=UUID("12345678-1234-1234-1234-123456789012"),
        )

        assert wallet.account_id == UUID("12345678-1234-1234-1234-123456789012")
        assert wallet.balance.amount == Decimal("0.00")
        assert wallet.currency == "BRL"

    def test_deposit_increases_wallet_balance(self):
        wallet = Wallet.create(
            account_id=UUID("12345678-1234-1234-1234-123456789012"),
        )

        wallet.deposit(Money(amount=Decimal("100.00")))

        assert wallet.balance.amount == Decimal("100.00")
        assert wallet.balance.currency == "BRL"

    def test_restore_wallet_preserves_balance_and_currency(self):
        wallet = Wallet.restore(
            wallet_id=UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
            account_id=UUID("12345678-1234-1234-1234-123456789012"),
            balance=Money(amount=Decimal("25.00"), currency="BRL"),
        )

        assert wallet.id == UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
        assert wallet.account_id == UUID("12345678-1234-1234-1234-123456789012")
        assert wallet.balance.amount == Decimal("25.00")
