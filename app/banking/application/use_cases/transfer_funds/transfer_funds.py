from app.banking.application.exceptions.invalid_transfer_amount_exception import (
    InvalidTransferAmountException,
)
from app.banking.application.exceptions.same_wallet_transfer_exception import (
    SameWalletTransferException,
)
from app.banking.domain.entities.ledger_entry import LedgerEntry
from app.banking.domain.entities.transaction import Transaction
from app.banking.domain.repositories.ledger_entry_repository import (
    LedgerEntryRepository,
)
from app.banking.domain.repositories.transaction_repository import TransactionRepository
from app.banking.domain.repositories.wallet_repository import WalletRepository
from app.shared.application.unit_of_work import UnitOfWork
from app.shared.domain.exceptions.not_found_exception import NotFoundException

from .transfer_funds_input import TransferFundsInput
from .transfer_funds_output import TransferFundsOutput


class TransferFunds:
    def __init__(
        self,
        unit_of_work: UnitOfWork,
        wallet_repository: WalletRepository,
        transaction_repository: TransactionRepository,
        ledger_entry_repository: LedgerEntryRepository,
    ) -> None:
        self._unit_of_work = unit_of_work
        self._wallet_repository = wallet_repository
        self._transaction_repository = transaction_repository
        self._ledger_entry_repository = ledger_entry_repository

    def execute(
        self,
        input_data: TransferFundsInput,
    ) -> TransferFundsOutput:
        if input_data.source_wallet_id == input_data.destination_wallet_id:
            raise SameWalletTransferException()

        if input_data.amount.is_positive() is False:
            raise InvalidTransferAmountException()

        with self._unit_of_work as uow:
            existing_transaction = None

            if input_data.idempotency_key:
                existing_transaction = (
                    self._transaction_repository.find_by_idempotency_key(
                        input_data.idempotency_key
                    )
                )

            if existing_transaction is not None:
                return TransferFundsOutput(
                    transaction_id=existing_transaction.id,
                    source_wallet_id=input_data.source_wallet_id,
                    destination_wallet_id=input_data.destination_wallet_id,
                    amount=existing_transaction.amount,
                    transaction_type=existing_transaction.type,
                    status=existing_transaction.status,
                )

            ordered_wallet_ids = sorted(
                [input_data.source_wallet_id, input_data.destination_wallet_id],
                key=str,
            )
            first_wallet = self._wallet_repository.find_by_id_for_update(
                ordered_wallet_ids[0]
            )
            second_wallet = self._wallet_repository.find_by_id_for_update(
                ordered_wallet_ids[1]
            )

            if first_wallet is None or second_wallet is None:
                raise NotFoundException("Wallet not found")

            wallets_by_id = {
                first_wallet.id: first_wallet,
                second_wallet.id: second_wallet,
            }
            source_wallet = wallets_by_id[input_data.source_wallet_id]
            destination_wallet = wallets_by_id[input_data.destination_wallet_id]

            source_wallet.withdraw(input_data.amount)
            destination_wallet.deposit(input_data.amount)

            transaction = Transaction.create_transfer(
                amount=input_data.amount,
                payer_account_id=source_wallet.account_id,
                payee_account_id=destination_wallet.account_id,
                idempotency_key=input_data.idempotency_key,
            )

            entries = [
                LedgerEntry.create_debit(
                    transaction_id=transaction.id,
                    wallet_id=source_wallet.id,
                    amount=input_data.amount,
                ),
                LedgerEntry.create_credit(
                    transaction_id=transaction.id,
                    wallet_id=destination_wallet.id,
                    amount=input_data.amount,
                ),
            ]

            self._wallet_repository.save(source_wallet)
            self._wallet_repository.save(destination_wallet)
            self._transaction_repository.save(transaction)
            self._ledger_entry_repository.save_many(entries)
            uow.commit()

            return TransferFundsOutput(
                transaction_id=transaction.id,
                source_wallet_id=source_wallet.id,
                destination_wallet_id=destination_wallet.id,
                amount=transaction.amount,
                transaction_type=transaction.type,
                status=transaction.status,
            )
