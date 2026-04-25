from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.banking.domain.entities.transaction import Transaction
from app.banking.domain.enums.transaction_status import TransactionStatus
from app.banking.domain.enums.transaction_type import TransactionType
from app.banking.domain.repositories.transaction_repository import TransactionRepository
from app.banking.domain.value_objects.money import Money
from app.banking.infrastructure.repositories.transaction_model import TransactionModel


class TransactionRepositoryImpl(TransactionRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def find_by_id(self, transaction_id: UUID) -> Transaction | None:
        stmt = select(TransactionModel).where(TransactionModel.id == transaction_id)
        model = self._session.scalar(stmt)
        if model is None:
            return None
        return self._to_entity(model)

    def find_by_idempotency_key(self, idempotency_key: str) -> Transaction | None:
        stmt = select(TransactionModel).where(
            TransactionModel.idempotency_key == idempotency_key
        )
        model = self._session.scalar(stmt)
        if model is None:
            return None
        return self._to_entity(model)

    def save(self, transaction: Transaction) -> None:
        model = self._to_model(transaction)
        self._session.merge(model)
        self._session.flush()

    def _to_entity(self, model: TransactionModel) -> Transaction:
        return Transaction(
            transaction_id=model.id,
            transaction_type=TransactionType(model.type),
            transaction_status=TransactionStatus(model.status),
            transaction_amount=Money(
                amount=Decimal(model.amount),
                currency=model.currency,
            ),
            idempotency_key=model.idempotency_key,
            payer_account_id=model.payer_account_id,
            payee_account_id=model.payee_account_id,
            created_at=model.created_at,
        )

    def _to_model(self, transaction: Transaction) -> TransactionModel:
        return TransactionModel(
            id=transaction.id,
            type=transaction.type.value,
            status=transaction.status.value,
            amount=str(transaction.amount.amount),
            currency=transaction.amount.currency,
            idempotency_key=transaction.idempotency_key,
            payer_account_id=transaction.payer_account_id,
            payee_account_id=transaction.payee_account_id,
            created_at=transaction.created_at,
        )
