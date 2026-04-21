from app.shared.domain.exceptions import DomainException


class InvalidMoneyAmountException(DomainException):
    def __init__(self, message: str = "Invalid money amount") -> None:
        super().__init__(message)
