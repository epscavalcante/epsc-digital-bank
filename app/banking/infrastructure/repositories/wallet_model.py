from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.identity.infrastructure.database import Base


class WalletModel(Base):
    __tablename__ = "wallets"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    account_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("accounts.id"),
        unique=True,
        index=True,
    )
    balance_amount: Mapped[str] = mapped_column(String(50), default="0.00")
    balance_currency: Mapped[str] = mapped_column(String(3), default="BRL")
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )
