import os
from contextlib import asynccontextmanager
from uuid import UUID

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.api.schemas import (
    DepositFundsRequest,
    DepositFundsResponse,
    ErrorResponse,
    HealthResponse,
    MoneyResponse,
    SignupRequest,
    SignupResponse,
)
from app.banking.application.exceptions.account_cant_deposit_funds_exception import (
    AccountCantDepositFundsException,
)
from app.banking.application.exceptions.invalid_deposit_amount_exception import (
    InvalidDepositAmountException,
)
from app.banking.application.use_cases.deposit_funds.deposit_funds import DepositFunds
from app.banking.application.use_cases.deposit_funds.deposit_funds_input import (
    DepositFundsInput,
)
from app.banking.domain.exceptions.invalid_money_amount_exception import (
    InvalidMoneyAmountException,
)
from app.banking.domain.value_objects.money import Money
from app.identity.application.exceptions.account_not_found_exception import (
    AccountNotFoundException,
)
from app.identity.application.use_cases.signup.signup import Signup
from app.identity.application.use_cases.signup.signup_input import SignupInput
from app.identity.domain.exceptions.invalid_cpf_exception import InvalidCPFException
from app.identity.domain.exceptions.invalid_email_exception import InvalidEmailException
from app.identity.domain.exceptions.invalid_name_exception import InvalidNameException
from app.identity.infrastructure.database import Database
from app.shared.domain.exceptions import AlreadyExistsException, DomainException
from app.shared.infrastructure.sqlalchemy_unit_of_work import SqlAlchemyUnitOfWork


def create_app(database_url: str | None = None) -> FastAPI:
    if database_url is not None:
        resolved_database_url = database_url
    else:
        resolved_database_url = os.getenv(
            "DATABASE_URL",
            "sqlite:///./epsc-digital-bank.db",
        )
    database = Database(resolved_database_url)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.database = database
        database.create_tables()
        yield
        database.dispose()

    app = FastAPI(
        title="EPSC Digital Bank API",
        version="0.1.0",
        lifespan=lifespan,
    )

    @app.exception_handler(AccountNotFoundException)
    async def handle_not_found(_: Request, exc: AccountNotFoundException):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=ErrorResponse(detail=str(exc)).model_dump(),
        )

    @app.exception_handler(AlreadyExistsException)
    async def handle_already_exists(_: Request, exc: AlreadyExistsException):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=ErrorResponse(detail=str(exc)).model_dump(),
        )

    @app.exception_handler(
        InvalidCPFException,
    )
    @app.exception_handler(
        InvalidEmailException,
    )
    @app.exception_handler(
        InvalidNameException,
    )
    @app.exception_handler(
        InvalidMoneyAmountException,
    )
    @app.exception_handler(
        InvalidDepositAmountException,
    )
    @app.exception_handler(
        AccountCantDepositFundsException,
    )
    async def handle_bad_request(_: Request, exc: DomainException):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=ErrorResponse(detail=str(exc)).model_dump(),
        )

    @app.get(
        "/health",
        response_model=HealthResponse,
    )
    async def healthcheck() -> HealthResponse:
        return HealthResponse(status="ok")

    @app.post(
        "/accounts",
        response_model=SignupResponse,
        status_code=status.HTTP_201_CREATED,
        responses={
            status.HTTP_409_CONFLICT: {"model": ErrorResponse},
            status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse},
        },
    )
    async def signup_account(payload: SignupRequest) -> SignupResponse:
        uow = SqlAlchemyUnitOfWork(app.state.database)
        use_case = Signup(unit_of_work=uow)
        result = use_case.execute(
            SignupInput(
                tax_id=payload.tax_id,
                name=payload.name,
                email=payload.email,
            )
        )
        return SignupResponse(account_id=result.account_id)

    @app.post(
        "/accounts/{account_id}/deposits",
        response_model=DepositFundsResponse,
        status_code=status.HTTP_201_CREATED,
        responses={
            status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
            status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse},
        },
    )
    async def deposit_funds(
        account_id: UUID,
        payload: DepositFundsRequest,
    ) -> DepositFundsResponse:
        uow = SqlAlchemyUnitOfWork(app.state.database)
        use_case = DepositFunds(unit_of_work=uow)
        result = use_case.execute(
            DepositFundsInput(
                account_id=account_id,
                amount=Money(amount=payload.amount),
                idempotency_key=payload.idempotency_key,
            )
        )
        return DepositFundsResponse(
            transaction_id=result.transaction_id,
            account_id=result.account_id,
            amount=MoneyResponse(
                amount=result.amount.amount, currency=result.amount.currency
            ),
            transaction_type=result.transaction_type.value,
            status=result.status.value,
        )

    return app


app = create_app()
