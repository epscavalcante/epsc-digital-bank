from app.shared.domain.exceptions import AlreadyExistsException


class AccountNotFoundException(AlreadyExistsException):
    def __init__(self, message: str = "Account not found") -> None:
        super().__init__(message)
