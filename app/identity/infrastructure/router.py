from fastapi import APIRouter, Request, status

from app.api.schemas import ErrorResponse, SignupRequest, SignupResponse
from app.identity.application.use_cases.signup.signup import Signup
from app.identity.application.use_cases.signup.signup_input import SignupInput
from app.shared.infrastructure.sqlalchemy_unit_of_work import SqlAlchemyUnitOfWork

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
def signup_account(request: Request, payload: SignupRequest) -> SignupResponse:
    uow = SqlAlchemyUnitOfWork(request.app.state.database)
    use_case = Signup(unit_of_work=uow)
    result = use_case.execute(
        SignupInput(
            tax_id=payload.tax_id,
            name=payload.name,
            email=payload.email,
        )
    )
    return SignupResponse(account_id=result.account_id)
