from app.shared.domain.exceptions import DomainException


class CurrencyMismatchException(DomainException):
    def __init__(self, message: str = "Currency mismatch") -> None:
        super().__init__(message)
