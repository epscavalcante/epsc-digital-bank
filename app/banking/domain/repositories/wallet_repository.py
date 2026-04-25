from typing import Protocol
from uuid import UUID

from app.banking.domain.entities.wallet import Wallet


class WalletRepository(Protocol):
    def find_by_id(self, wallet_id: UUID) -> Wallet | None: ...
    def find_by_account_id(self, account_id: UUID) -> Wallet | None: ...
    def save(self, wallet: Wallet) -> None: ...
