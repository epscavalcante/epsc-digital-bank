from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.banking.domain.entities.wallet import Wallet
from app.banking.domain.repositories.wallet_repository import WalletRepository
from app.banking.domain.value_objects.money import Money
from app.banking.infrastructure.repositories.wallet_model import WalletModel


class WalletRepositoryImpl(WalletRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def find_by_id(self, wallet_id: UUID) -> Wallet | None:
        stmt = select(WalletModel).where(WalletModel.id == wallet_id)
        model = self._session.scalar(stmt)
        if model is None:
            return None
        return self._to_entity(model)

    def find_by_account_id(self, account_id: UUID) -> Wallet | None:
        stmt = select(WalletModel).where(WalletModel.account_id == account_id)
        model = self._session.scalar(stmt)
        if model is None:
            return None
        return self._to_entity(model)

    def save(self, wallet: Wallet) -> None:
        model = self._to_model(wallet)
        self._session.merge(model)
        self._session.flush()

    def _to_entity(self, model: WalletModel) -> Wallet:
        return Wallet.restore(
            wallet_id=model.id,
            account_id=model.account_id,
            balance=Money(
                amount=Decimal(model.balance_amount),
                currency=model.balance_currency,
            ),
        )

    def _to_model(self, wallet: Wallet) -> WalletModel:
        return WalletModel(
            id=wallet.id,
            account_id=wallet.account_id,
            balance_amount=str(wallet.balance.amount),
            balance_currency=wallet.balance.currency,
        )
