from dataclasses import dataclass

from app.identity.domain.exceptions.invalid_name_exception import InvalidNameException


@dataclass(frozen=True)
class Name:
    value: str

    def __post_init__(self) -> None:
        if not self.value or not self.value.strip():
            raise InvalidNameException()

        object.__setattr__(self, "value", self.value.strip())

    def __str__(self) -> str:
        return self.value
