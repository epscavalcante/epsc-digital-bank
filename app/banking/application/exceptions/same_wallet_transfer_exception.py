from app.shared.domain.exceptions import DomainException


class SameWalletTransferException(DomainException):
    def __init__(self, message: str = "Cannot transfer to the same wallet") -> None:
        super().__init__(message)
