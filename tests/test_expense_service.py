"""Tests for expense service."""

from decimal import Decimal

import pytest
from sqlalchemy.orm import Session

from src.services import trip_service, participant_service, expense_service


def _setup_trip(session: Session) -> tuple[int, list[str]]:
    """Create a trip with 3 participants."""
    trip = trip_service.create_trip(session, "Trip")
    names = ["Anna", "Ben", "Clara"]
    for n in names:
        participant_service.add_participant(session, trip.id, n)
    return trip.id, names


def test_add_expense_for_all(session: Session) -> None:
    trip_id, _ = _setup_trip(session)
    exp = expense_service.add_expense(
        session, trip_id, "Anna", Decimal("120"), "Dinner"
    )
    assert exp.amount == Decimal("120")
    assert len(exp.splits) == 3
    assert exp.splits[0].share_amount == Decimal("40")


def test_add_expense_for_subset(session: Session) -> None:
    trip_id, _ = _setup_trip(session)
    exp = expense_service.add_expense(
        session, trip_id, "Ben", Decimal("30"), "Taxi", ["Ben", "Clara"]
    )
    assert len(exp.splits) == 2
    assert exp.splits[0].share_amount == Decimal("15")


def test_round_to_05(session: Session) -> None:
    from src.services.expense_service import round_to_05

    assert round_to_05(Decimal("33.33")) == Decimal("33.35")
    assert round_to_05(Decimal("33.37")) == Decimal("33.35")
    assert round_to_05(Decimal("33.38")) == Decimal("33.40")
    assert round_to_05(Decimal("10.00")) == Decimal("10.00")
    assert round_to_05(Decimal("10.02")) == Decimal("10.00")
    assert round_to_05(Decimal("10.03")) == Decimal("10.05")


def test_edit_expense(session: Session) -> None:
    trip_id, _ = _setup_trip(session)
    exp = expense_service.add_expense(
        session, trip_id, "Anna", Decimal("90"), "Lunch"
    )
    updated = expense_service.edit_expense(
        session, exp.id, amount=Decimal("120"), description="Big Lunch"
    )
    assert updated.description == "Big Lunch"
    assert updated.amount == Decimal("120")
    assert updated.splits[0].share_amount == Decimal("40")


def test_delete_expense(session: Session) -> None:
    trip_id, _ = _setup_trip(session)
    exp = expense_service.add_expense(
        session, trip_id, "Anna", Decimal("50"), "Snacks"
    )
    desc = expense_service.delete_expense(session, exp.id)
    assert desc == "Snacks"
    assert expense_service.list_expenses(session, trip_id) == []


def test_expense_on_closed_trip(session: Session) -> None:
    trip_id, _ = _setup_trip(session)
    trip_service.close_trip(session, trip_id)
    with pytest.raises(ValueError, match="closed"):
        expense_service.add_expense(
            session, trip_id, "Anna", Decimal("50"), "Nope"
        )
