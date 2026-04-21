from app.shared.domain.exceptions import DomainException


class InvalidDepositAmountException(DomainException):
    def __init__(self, message: str = "Invalid deposit amount") -> None:
        super().__init__(message)
