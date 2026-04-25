from app.shared.domain.exceptions.domain_exception import DomainException


class NotFoundException(DomainException):
    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__(message)
