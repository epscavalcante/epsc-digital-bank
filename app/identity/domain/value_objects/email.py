from dataclasses import dataclass

from app.identity.domain.exceptions.invalid_email_exception import InvalidEmailException


@dataclass(frozen=True, slots=True)
class Email:
    value: str

    def __post_init__(self) -> None:
        normalized_value = self.value.strip().lower()

        if "@" not in normalized_value:
            raise InvalidEmailException()

        object.__setattr__(self, "value", normalized_value)

    def __str__(self) -> str:
        return self.value
