from uuid import UUID

from fastapi import APIRouter, Header, Request, status

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
from app.banking.domain.value_objects.money import Money
from app.shared.infrastructure.sqlalchemy_unit_of_work import SqlAlchemyUnitOfWork

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
    request: Request,
    wallet_id: UUID,
    payload: DepositFundsRequest,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
) -> DepositFundsResponse:
    uow = SqlAlchemyUnitOfWork(request.app.state.database)
    use_case = DepositFunds(unit_of_work=uow)
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
    request: Request,
    wallet_id: UUID,
    payload: TransferFundsRequest,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
) -> TransferFundsResponse:
    uow = SqlAlchemyUnitOfWork(request.app.state.database)
    use_case = TransferFunds(unit_of_work=uow)
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
