from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


class Base(DeclarativeBase):
    pass


class Database:
    def __init__(self, database_url: str) -> None:
        self._engine = create_engine(database_url, echo=False)
        self._session_factory = sessionmaker(bind=self._engine)

    def dispose(self) -> None:
        self._engine.dispose()

    def create_tables(self) -> None:
        Base.metadata.create_all(self._engine)

    def drop_tables(self) -> None:
        Base.metadata.drop_all(self._engine)

    def get_session(self) -> Session:
        return self._session_factory()
