from dataclasses import dataclass
from uuid import UUID


@dataclass(slots=True, frozen=True)
class SignupOutput:
    account_id: UUID
