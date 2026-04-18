from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class SignupInput:
    tax_id: str
    name: str
    email: str
