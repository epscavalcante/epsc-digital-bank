from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.banking.domain.value_objects.money import Money
from app.identity.domain.entities.account import Account
from app.identity.domain.enums.account_status import AccountStatus
from app.identity.domain.repositories.account_repository import AccountRepository
from app.identity.domain.value_objects.cpf import CPF
from app.identity.domain.value_objects.email import Email
from app.identity.domain.value_objects.name import Name
from app.identity.infrastructure.repositories.account_model import AccountModel


class AccountRepositoryImpl(AccountRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def find_by_id(self, account_id: UUID) -> Account | None:
        stmt = select(AccountModel).where(AccountModel.id == account_id)
        model = self._session.scalar(stmt)
        if model is None:
            return None
        return self._to_entity(model)

    def find_by_email(self, email: Email) -> Account | None:
        stmt = select(AccountModel).where(AccountModel.email == email.value)
        model = self._session.scalar(stmt)
        if model is None:
            return None
        return self._to_entity(model)

    def find_by_tax_id(self, tax_id: CPF) -> Account | None:
        stmt = select(AccountModel).where(AccountModel.tax_id == tax_id.value)
        model = self._session.scalar(stmt)
        if model is None:
            return None
        return self._to_entity(model)

    def save(self, account: Account) -> None:
        model = self._to_model(account)
        self._session.merge(model)
        self._session.flush()

    def _to_entity(self, model: AccountModel) -> Account:
        return Account(
            account_id=model.id,
            tax_id=CPF(value=model.tax_id),
            name=Name(value=model.name),
            email=Email(value=model.email),
            balance=Money(
                amount=Decimal(model.balance_amount),
                currency=model.balance_currency,
            ),
            status=AccountStatus(model.status),
        )

    def _to_model(self, account: Account) -> AccountModel:
        return AccountModel(
            id=account.id,
            tax_id=account.tax_id.value,
            name=account.name.value,
            email=account.email.value,
            balance_amount=str(account.balance.amount),
            balance_currency=account.balance.currency,
            status=account.status.value,
        )
