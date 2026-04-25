from typing import cast

from sqlalchemy.orm import Session

from app.banking.infrastructure.repositories.ledger_entry_repository_impl import (
    LedgerEntryRepositoryImpl,
)
from app.banking.infrastructure.repositories.transaction_repository_impl import (
    TransactionRepositoryImpl,
)
from app.identity.infrastructure.database import Database
from app.identity.infrastructure.repositories.account_repository_impl import (
    AccountRepositoryImpl,
)
from app.shared.application.unit_of_work import UnitOfWork


class SqlAlchemyUnitOfWork(UnitOfWork):
    def __init__(self, database: Database) -> None:
        self._database = database
        self._session: Session | None = None
        self.account_repository = cast(AccountRepositoryImpl, None)
        self.transaction_repository = cast(TransactionRepositoryImpl, None)
        self.ledger_entry_repository = cast(LedgerEntryRepositoryImpl, None)

    def __enter__(self) -> "SqlAlchemyUnitOfWork":
        self._session = self._database.get_session()
        self.account_repository = AccountRepositoryImpl(self._session)
        self.transaction_repository = TransactionRepositoryImpl(self._session)
        self.ledger_entry_repository = LedgerEntryRepositoryImpl(self._session)
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        if self._session is None:
            return

        try:
            if exc_type is not None:
                self.rollback()
        finally:
            self._session.close()
            self._session = None

    def commit(self) -> None:
        if self._session is None:
            raise RuntimeError("UnitOfWork must be entered before commit")
        self._session.commit()

    def rollback(self) -> None:
        if self._session is None:
            raise RuntimeError("UnitOfWork must be entered before rollback")
        self._session.rollback()
