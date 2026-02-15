"""Expense and ExpenseSplit models."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db import Base


class Expense(Base):
    """An expense paid by one participant for one or more participants."""

    __tablename__ = "expenses"

    id: Mapped[int] = mapped_column(primary_key=True)
    trip_id: Mapped[int] = mapped_column(ForeignKey("trips.id", ondelete="CASCADE"))
    paid_by_id: Mapped[int] = mapped_column(
        ForeignKey("participants.id", ondelete="CASCADE")
    )
    description: Mapped[str] = mapped_column(String(300))
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    trip: Mapped["Trip"] = relationship(back_populates="expenses")
    paid_by_participant: Mapped["Participant"] = relationship(
        back_populates="expenses_paid"
    )
    splits: Mapped[list["ExpenseSplit"]] = relationship(
        back_populates="expense", cascade="all, delete-orphan"
    )


class ExpenseSplit(Base):
    """A single participant's share of an expense."""

    __tablename__ = "expense_splits"

    id: Mapped[int] = mapped_column(primary_key=True)
    expense_id: Mapped[int] = mapped_column(
        ForeignKey("expenses.id", ondelete="CASCADE")
    )
    participant_id: Mapped[int] = mapped_column(
        ForeignKey("participants.id", ondelete="CASCADE")
    )
    share_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))

    expense: Mapped["Expense"] = relationship(back_populates="splits")
    participant: Mapped["Participant"] = relationship(back_populates="splits")


from src.models.trip import Trip  # noqa: E402
from src.models.participant import Participant  # noqa: E402
