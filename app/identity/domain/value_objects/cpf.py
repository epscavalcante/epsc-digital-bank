import re
from dataclasses import dataclass
from typing import ClassVar

from app.identity.domain.exceptions.invalid_cpf_exception import InvalidCPFException


@dataclass(frozen=True)
class CPF:
    value: str

    MAX_LENGTH: ClassVar[int] = 11
    INVALID_PATTERNS: ClassVar[set[str]] = {str(i) * 11 for i in range(10)}

    def __post_init__(self) -> None:
        clean_value = re.sub(r"\D", "", str(self.value))

        if len(clean_value) != self.MAX_LENGTH:
            raise InvalidCPFException(
                f"CPF deve ter 11 dígitos, got {len(clean_value)}"
            )

        if clean_value in self.INVALID_PATTERNS:
            raise InvalidCPFException(f"Padrão inválido: {clean_value}")

        if not self._validate_digits(clean_value):
            raise InvalidCPFException(f"Dígitos verificadores inválidos: {clean_value}")

        object.__setattr__(self, "value", clean_value)

    def _validate_digits(self, value: str) -> bool:
        s1 = sum(int(value[i]) * (10 - i) for i in range(9))
        d1 = (s1 * 10) % 11
        d1 = 0 if d1 == 10 else d1

        s2 = sum(int(value[i]) * (11 - i) for i in range(10))
        d2 = (s2 * 10) % 11
        d2 = 0 if d2 == 10 else d2

        return int(value[9]) == d1 and int(value[10]) == d2
