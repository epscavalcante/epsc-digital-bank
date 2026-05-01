from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.dependencies import (
    get_account_repository,
    get_uow,
    get_wallet_repository,
)
from app.api.schemas import ErrorResponse, SignupRequest, SignupResponse
from app.banking.domain.repositories.wallet_repository import WalletRepository
from app.identity.application.use_cases.signup.signup import Signup
from app.identity.application.use_cases.signup.signup_input import SignupInput
from app.identity.domain.repositories.account_repository import AccountRepository
from app.shared.application.unit_of_work import UnitOfWork

router = APIRouter(tags=["Identity"])


@router.post(
    "/accounts",
    response_model=SignupResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_409_CONFLICT: {"model": ErrorResponse},
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse},
    },
)
def signup_account(
    payload: SignupRequest,
    uow: Annotated[UnitOfWork, Depends(get_uow)],
    account_repository: Annotated[AccountRepository, Depends(get_account_repository)],
    wallet_repository: Annotated[WalletRepository, Depends(get_wallet_repository)],
) -> SignupResponse:
    use_case = Signup(
        unit_of_work=uow,
        account_repository=account_repository,
        wallet_repository=wallet_repository,
    )
    result = use_case.execute(
        SignupInput(
            tax_id=payload.tax_id,
            name=payload.name,
            email=payload.email,
        )
    )
    return SignupResponse(account_id=result.account_id)
