from app.shared.domain.exceptions import DomainException


class InsufficientFundsException(DomainException):
    def __init__(self, message: str = "Insufficient funds") -> None:
        super().__init__(message)
