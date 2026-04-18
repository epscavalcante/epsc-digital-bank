from app.shared.domain.exceptions import DomainException


class InvalidNameException(DomainException):
    def __init__(self, message: str = "Invalid Name") -> None:
        super().__init__(message)
