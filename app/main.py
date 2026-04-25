import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.api.schemas import (
    ErrorResponse,
    HealthResponse,
)
from app.banking.application.exceptions.account_cant_deposit_funds_exception import (
    AccountCantDepositFundsException,
)
from app.banking.application.exceptions.invalid_deposit_amount_exception import (
    InvalidDepositAmountException,
)
from app.banking.domain.exceptions.invalid_money_amount_exception import (
    InvalidMoneyAmountException,
)
from app.banking.infrastructure.router import router as banking_router
from app.identity.application.exceptions.account_not_found_exception import (
    AccountNotFoundException,
)
from app.identity.domain.exceptions.invalid_cpf_exception import InvalidCPFException
from app.identity.domain.exceptions.invalid_email_exception import InvalidEmailException
from app.identity.domain.exceptions.invalid_name_exception import InvalidNameException
from app.identity.infrastructure.database import Database
from app.identity.infrastructure.router import router as identity_router
from app.shared.domain.exceptions import AlreadyExistsException, DomainException


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

    app.include_router(identity_router)
    app.include_router(banking_router)

    return app


app = create_app()
