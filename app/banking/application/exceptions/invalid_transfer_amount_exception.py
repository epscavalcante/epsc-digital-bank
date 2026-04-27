from app.shared.domain.exceptions import DomainException


class InvalidTransferAmountException(DomainException):
    def __init__(self, message: str = "Invalid transfer amount") -> None:
        super().__init__(message)
