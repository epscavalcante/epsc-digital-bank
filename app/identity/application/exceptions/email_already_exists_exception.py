from app.shared.domain.exceptions import AlreadyExistsException


class EmailAlreadyExistsException(AlreadyExistsException):
    def __init__(self, message: str = "Email already exists") -> None:
        super().__init__(message)
