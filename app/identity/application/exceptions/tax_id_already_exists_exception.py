from app.shared.domain.exceptions import AlreadyExistsException


class TaxIdAlreadyExistsException(AlreadyExistsException):
    def __init__(self, message: str = "Tax ID already exists") -> None:
        super().__init__(message)
