from enum import StrEnum


class AccountStatus(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    BLOCKED = "blocked"
    PENDING_APPROVAL = "pending_approval"
    SUSPENDED = "suspended"
