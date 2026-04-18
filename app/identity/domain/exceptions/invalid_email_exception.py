from app.shared.domain.exceptions import DomainException


class InvalidEmailException(DomainException):
    def __init__(self) -> None:
        super().__init__("Invalid email")
