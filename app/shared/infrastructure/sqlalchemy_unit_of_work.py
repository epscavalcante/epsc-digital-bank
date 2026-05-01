from typing import cast

from sqlalchemy.orm import Session

from app.identity.infrastructure.database import Database
from app.shared.application.unit_of_work import UnitOfWork


class SqlAlchemyUnitOfWork(UnitOfWork):
    def __init__(self, database_or_session: Database | Session) -> None:
        self._database: Database | None = None
        self._session: Session | None = None
        self._owns_session = isinstance(database_or_session, Database)

        if self._owns_session:
            self._database = cast(Database, database_or_session)
        else:
            self._session = cast(Session, database_or_session)

    def __enter__(self) -> "SqlAlchemyUnitOfWork":
        if self._session is None:
            if self._database is None:
                raise RuntimeError("UnitOfWork has no database or session")
            self._session = self._database.get_session()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        if self._session is None:
            return

        try:
            if exc_type is not None:
                self.rollback()
        finally:
            if self._owns_session:
                self._session.close()
                self._session = None

    @property
    def session(self) -> Session:
        if self._session is None:
            raise RuntimeError("UnitOfWork must be entered before accessing session")
        return self._session

    def commit(self) -> None:
        if self._session is None:
            raise RuntimeError("UnitOfWork must be entered before commit")
        self._session.commit()

    def rollback(self) -> None:
        if self._session is None:
            raise RuntimeError("UnitOfWork must be entered before rollback")
        self._session.rollback()
