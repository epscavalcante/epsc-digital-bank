from app.shared.domain.exceptions.domain_exception import DomainException


class AlreadyExistsException(DomainException):
    def __init__(self, message: str = "Resource already exists") -> None:
        super().__init__(message)
