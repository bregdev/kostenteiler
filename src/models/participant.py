"""Participant model."""

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db import Base


class Participant(Base):
    """A participant in a trip."""

    __tablename__ = "participants"
    __table_args__ = (
        UniqueConstraint("trip_id", "name", name="uq_participant_trip_name"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    trip_id: Mapped[int] = mapped_column(ForeignKey("trips.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(100))

    trip: Mapped["Trip"] = relationship(back_populates="participants")
    expenses_paid: Mapped[list["Expense"]] = relationship(back_populates="paid_by_participant")
    splits: Mapped[list["ExpenseSplit"]] = relationship(back_populates="participant")


from src.models.trip import Trip  # noqa: E402
from src.models.expense import Expense, ExpenseSplit  # noqa: E402
