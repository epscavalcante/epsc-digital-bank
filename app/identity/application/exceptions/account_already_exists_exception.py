from app.shared.domain.exceptions import AlreadyExistsException


class AccountAlreadyExistsException(AlreadyExistsException):
    def __init__(self, message: str = "Account already exists") -> None:
        super().__init__(message)
