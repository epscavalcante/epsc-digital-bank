from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.banking.domain.repositories.ledger_entry_repository import (
    LedgerEntryRepository,
)
from app.banking.domain.repositories.transaction_repository import (
    TransactionRepository,
)
from app.banking.domain.repositories.wallet_repository import WalletRepository
from app.banking.infrastructure.repositories.ledger_entry_repository_impl import (
    LedgerEntryRepositoryImpl,
)
from app.banking.infrastructure.repositories.transaction_repository_impl import (
    TransactionRepositoryImpl,
)
from app.banking.infrastructure.repositories.wallet_repository_impl import (
    WalletRepositoryImpl,
)
from app.identity.domain.repositories.account_repository import AccountRepository
from app.identity.infrastructure.repositories.account_repository_impl import (
    AccountRepositoryImpl,
)
from app.shared.application.unit_of_work import UnitOfWork
from app.shared.infrastructure.sqlalchemy_unit_of_work import SqlAlchemyUnitOfWork


def get_session(request: Request) -> Iterator[Session]:
    session = request.app.state.database.get_session()
    try:
        yield session
    finally:
        session.close()


def get_uow(session: Annotated[Session, Depends(get_session)]) -> UnitOfWork:
    return SqlAlchemyUnitOfWork(session)


def get_account_repository(
    uow: Annotated[UnitOfWork, Depends(get_uow)],
) -> AccountRepository:
    return AccountRepositoryImpl(uow.session)


def get_wallet_repository(
    uow: Annotated[UnitOfWork, Depends(get_uow)],
) -> WalletRepository:
    return WalletRepositoryImpl(uow.session)


def get_transaction_repository(
    uow: Annotated[UnitOfWork, Depends(get_uow)],
) -> TransactionRepository:
    return TransactionRepositoryImpl(uow.session)


def get_ledger_repository(
    uow: Annotated[UnitOfWork, Depends(get_uow)],
) -> LedgerEntryRepository:
    return LedgerEntryRepositoryImpl(uow.session)
