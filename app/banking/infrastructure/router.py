from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header, status

from app.api.dependencies import (
    get_ledger_repository,
    get_transaction_repository,
    get_uow,
    get_wallet_repository,
)
from app.api.schemas import (
    DepositFundsRequest,
    DepositFundsResponse,
    ErrorResponse,
    MoneyResponse,
    TransferFundsRequest,
    TransferFundsResponse,
)
from app.banking.application.use_cases.deposit_funds.deposit_funds import DepositFunds
from app.banking.application.use_cases.deposit_funds.deposit_funds_input import (
    DepositFundsInput,
)
from app.banking.application.use_cases.transfer_funds.transfer_funds import (
    TransferFunds,
)
from app.banking.application.use_cases.transfer_funds.transfer_funds_input import (
    TransferFundsInput,
)
from app.banking.domain.repositories.ledger_entry_repository import (
    LedgerEntryRepository,
)
from app.banking.domain.repositories.transaction_repository import TransactionRepository
from app.banking.domain.repositories.wallet_repository import WalletRepository
from app.banking.domain.value_objects.money import Money
from app.shared.application.unit_of_work import UnitOfWork

router = APIRouter(tags=["Banking"])


@router.post(
    "/wallets/{wallet_id}/deposits",
    response_model=DepositFundsResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse},
    },
)
def deposit_funds(
    wallet_id: UUID,
    payload: DepositFundsRequest,
    uow: Annotated[UnitOfWork, Depends(get_uow)],
    wallet_repository: Annotated[WalletRepository, Depends(get_wallet_repository)],
    transaction_repository: Annotated[
        TransactionRepository,
        Depends(get_transaction_repository),
    ],
    ledger_entry_repository: Annotated[
        LedgerEntryRepository,
        Depends(get_ledger_repository),
    ],
    idempotency_key: Annotated[str, Header(alias="Idempotency-Key")],
) -> DepositFundsResponse:
    use_case = DepositFunds(
        unit_of_work=uow,
        wallet_repository=wallet_repository,
        transaction_repository=transaction_repository,
        ledger_entry_repository=ledger_entry_repository,
    )
    result = use_case.execute(
        DepositFundsInput(
            wallet_id=wallet_id,
            amount=Money(amount=payload.amount),
            idempotency_key=idempotency_key,
        )
    )
    return DepositFundsResponse(
        transaction_id=result.transaction_id,
        wallet_id=result.wallet_id,
        amount=MoneyResponse(
            amount=result.amount.amount,
            currency=result.amount.currency,
        ),
        transaction_type=result.transaction_type.value,
        status=result.status.value,
    )


@router.post(
    "/wallets/{wallet_id}/transfers",
    response_model=TransferFundsResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse},
    },
)
def transfer_funds(
    wallet_id: UUID,
    payload: TransferFundsRequest,
    uow: Annotated[UnitOfWork, Depends(get_uow)],
    wallet_repository: Annotated[WalletRepository, Depends(get_wallet_repository)],
    transaction_repository: Annotated[
        TransactionRepository,
        Depends(get_transaction_repository),
    ],
    ledger_entry_repository: Annotated[
        LedgerEntryRepository,
        Depends(get_ledger_repository),
    ],
    idempotency_key: Annotated[str, Header(alias="Idempotency-Key")],
) -> TransferFundsResponse:
    use_case = TransferFunds(
        unit_of_work=uow,
        wallet_repository=wallet_repository,
        transaction_repository=transaction_repository,
        ledger_entry_repository=ledger_entry_repository,
    )
    result = use_case.execute(
        TransferFundsInput(
            source_wallet_id=wallet_id,
            destination_wallet_id=payload.destination_wallet_id,
            amount=Money(amount=payload.amount),
            idempotency_key=idempotency_key,
        )
    )
    return TransferFundsResponse(
        transaction_id=result.transaction_id,
        source_wallet_id=result.source_wallet_id,
        destination_wallet_id=result.destination_wallet_id,
        amount=MoneyResponse(
            amount=result.amount.amount,
            currency=result.amount.currency,
        ),
        transaction_type=result.transaction_type.value,
        status=result.status.value,
    )
