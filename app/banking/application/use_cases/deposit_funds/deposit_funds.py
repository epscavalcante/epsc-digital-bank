from app.identity.application.exceptions.account_not_found_exception import (
    AccountNotFoundException,
)
from app.banking.application.exceptions.account_cant_deposit_funds_exception import (
    AccountCantDepositFundsException,
)
from app.banking.application.exceptions.invalid_deposit_amount_exception import (
    InvalidDepositAmountException,
)
from app.banking.domain.entities.ledger_entry import LedgerEntry
from app.banking.domain.entities.transaction import Transaction
from app.banking.domain.repositories.ledger_entry_repository import (
    LedgerEntryRepository,
)
from app.banking.domain.repositories.transaction_repository import (
    TransactionRepository,
)
from app.identity.domain.repositories.account_repository import AccountRepository

from .deposit_funds_input import (
    DepositFundsInput,
)
from .deposit_funds_output import (
    DepositFundsOutput,
)


class DepositFunds:
    def __init__(
        self,
        account_repository: AccountRepository,
        transaction_repository: TransactionRepository,
        ledger_entry_repository: LedgerEntryRepository,
    ) -> None:
        self._account_repository = account_repository
        self._transaction_repository = transaction_repository
        self._ledger_entry_repository = ledger_entry_repository

    def execute(
        self,
        input_data: DepositFundsInput,
    ) -> DepositFundsOutput:
        account = self._account_repository.find_by_id(
            input_data.account_id,
        )

        if account is None:
            raise AccountNotFoundException()

        if input_data.amount.is_positive() is False:
            raise InvalidDepositAmountException()

        if account.can_deposit_funds() is False:
            raise AccountCantDepositFundsException()

        existing_transaction = None

        if input_data.idempotency_key:
            existing_transaction = self._transaction_repository.find_by_idempotency_key(
                input_data.idempotency_key,
            )

        if existing_transaction is not None:
            return DepositFundsOutput(
                transaction_id=existing_transaction.id,
                account_id=account.id,
                amount=existing_transaction.amount,
                transaction_type=existing_transaction.type,
                status=existing_transaction.status,
                # created_at=existing_transaction.created_at,
            )

        account.deposit(input_data.amount)

        transaction = Transaction.create_deposit(
            amount=input_data.amount,
            payee_account_id=account.id,
            idempotency_key=input_data.idempotency_key,
        )

        ledger_entry = LedgerEntry.create_credit(
            transaction_id=transaction.id,
            account_id=account.id,
            amount=input_data.amount,
        )

        self._account_repository.save(account)
        self._transaction_repository.save(transaction)
        self._ledger_entry_repository.save(ledger_entry)

        return DepositFundsOutput(
            transaction_id=transaction.id,
            account_id=account.id,
            amount=transaction.amount,
            transaction_type=transaction.type,
            status=transaction.status,
            # created_at=transaction.created_at,
        )
