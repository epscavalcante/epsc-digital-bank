from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.identity.infrastructure.database import Base


class LedgerEntryModel(Base):
    __tablename__ = "ledger_entries"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    transaction_id: Mapped[UUID] = mapped_column(Uuid, index=True)
    wallet_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("wallets.id"), index=True)
    entry_type: Mapped[str] = mapped_column(String(20), index=True)
    amount: Mapped[str] = mapped_column(String(50))
    currency: Mapped[str] = mapped_column(String(3), default="BRL")
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))
