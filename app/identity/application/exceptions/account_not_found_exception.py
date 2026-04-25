from app.shared.domain.exceptions import NotFoundException


class AccountNotFoundException(NotFoundException):
    def __init__(self, message: str = "Account not found") -> None:
        super().__init__(message)
