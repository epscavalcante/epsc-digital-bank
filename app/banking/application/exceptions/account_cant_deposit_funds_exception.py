from app.shared.domain.exceptions import DomainException


class AccountCantDepositFundsException(DomainException):
    def __init__(self, message: str = "Account cannot deposit funds") -> None:
        super().__init__(message)
