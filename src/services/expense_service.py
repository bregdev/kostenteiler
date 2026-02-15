"""Expense service for CRUD operations."""

from decimal import ROUND_HALF_UP, Decimal
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models import Expense, ExpenseSplit, Participant, Trip


def round_to_05(amount: Decimal) -> Decimal:
    """Round a decimal amount to the nearest 0.05 CHF."""
    return (amount * 20).quantize(Decimal("1"), rounding=ROUND_HALF_UP) / 20


def add_expense(
    session: Session,
    trip_id: int,
    paid_by_name: str,
    amount: Decimal,
    description: str,
    for_names: Optional[list[str]] = None,
) -> Expense:
    """Add an expense, split equally among participants.

    Args:
        session: DB session.
        trip_id: Trip ID.
        paid_by_name: Name of the paying participant.
        amount: Total amount in CHF.
        description: What the expense is for.
        for_names: List of participant names to split among. None = all.

    Returns:
        The created Expense.
    """
    trip = session.get(Trip, trip_id)
    if not trip:
        raise ValueError(f"Trip {trip_id} not found.")
    if not trip.is_open:
        raise ValueError(f"Trip '{trip.name}' is closed.")

    payer = _get_participant(session, trip_id, paid_by_name)

    if for_names:
        beneficiaries = [_get_participant(session, trip_id, n) for n in for_names]
    else:
        beneficiaries = list(
            session.execute(
                select(Participant).where(Participant.trip_id == trip_id)
            ).scalars()
        )

    if not beneficiaries:
        raise ValueError("No participants to split the expense among.")

    expense = Expense(
        trip_id=trip_id,
        paid_by_id=payer.id,
        description=description,
        amount=amount,
    )
    session.add(expense)
    session.flush()

    share = round_to_05(amount / len(beneficiaries))
    for participant in beneficiaries:
        split = ExpenseSplit(
            expense_id=expense.id,
            participant_id=participant.id,
            share_amount=share,
        )
        session.add(split)

    session.commit()
    session.refresh(expense)
    return expense


def edit_expense(
    session: Session,
    expense_id: int,
    amount: Optional[Decimal] = None,
    description: Optional[str] = None,
) -> Expense:
    """Edit an existing expense. Recalculates splits if amount changes."""
    expense = session.get(Expense, expense_id)
    if not expense:
        raise ValueError(f"Expense {expense_id} not found.")
    if not expense.trip.is_open:
        raise ValueError("Cannot edit expenses on a closed trip.")

    if description is not None:
        expense.description = description

    if amount is not None:
        expense.amount = amount
        share = round_to_05(amount / len(expense.splits))
        for split in expense.splits:
            split.share_amount = share

    session.commit()
    session.refresh(expense)
    return expense


def delete_expense(session: Session, expense_id: int) -> str:
    """Delete an expense. Returns description."""
    expense = session.get(Expense, expense_id)
    if not expense:
        raise ValueError(f"Expense {expense_id} not found.")
    if not expense.trip.is_open:
        raise ValueError("Cannot delete expenses on a closed trip.")
    desc = expense.description
    session.delete(expense)
    session.commit()
    return desc


def list_expenses(session: Session, trip_id: int) -> list[Expense]:
    """Return all expenses for a trip."""
    return list(
        session.execute(
            select(Expense)
            .where(Expense.trip_id == trip_id)
            .order_by(Expense.created_at)
        ).scalars()
    )


def _get_participant(
    session: Session, trip_id: int, name: str
) -> Participant:
    """Get participant by name or raise."""
    p = session.execute(
        select(Participant).where(
            Participant.trip_id == trip_id, Participant.name == name
        )
    ).scalar_one_or_none()
    if not p:
        raise ValueError(f"Participant '{name}' not found in this trip.")
    return p
