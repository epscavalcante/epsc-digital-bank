from app.shared.domain.exceptions import DomainException


class InvalidCPFException(DomainException):
    def __init__(self, message: str = "Invalid CPF") -> None:
        super().__init__(message)
