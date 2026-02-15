"""Tests for settlement service."""

from decimal import Decimal

from sqlalchemy.orm import Session

from src.services import trip_service, participant_service, expense_service
from src.services.settlement_service import calculate_settlements


def test_simple_settlement(session: Session) -> None:
    """Anna pays 90 for all 3 -> Ben and Clara each owe Anna 30."""
    trip = trip_service.create_trip(session, "Trip")
    for n in ["Anna", "Ben", "Clara"]:
        participant_service.add_participant(session, trip.id, n)

    expense_service.add_expense(
        session, trip.id, "Anna", Decimal("90"), "Dinner"
    )

    transfers = calculate_settlements(session, trip.id)
    assert len(transfers) == 2
    total_to_anna = sum(t.amount for t in transfers if t.to_name == "Anna")
    assert total_to_anna == Decimal("60")


def test_no_expenses(session: Session) -> None:
    trip = trip_service.create_trip(session, "Trip")
    participant_service.add_participant(session, trip.id, "Anna")
    transfers = calculate_settlements(session, trip.id)
    assert transfers == []


def test_already_even(session: Session) -> None:
    """Each pays their share -- no transfers needed."""
    trip = trip_service.create_trip(session, "Trip")
    for n in ["Anna", "Ben"]:
        participant_service.add_participant(session, trip.id, n)

    expense_service.add_expense(
        session, trip.id, "Anna", Decimal("50"), "Dinner", ["Anna"]
    )
    expense_service.add_expense(
        session, trip.id, "Ben", Decimal("50"), "Drinks", ["Ben"]
    )

    transfers = calculate_settlements(session, trip.id)
    assert transfers == []


def test_multiple_expenses(session: Session) -> None:
    """Multiple expenses between 3 people."""
    trip = trip_service.create_trip(session, "Trip")
    for n in ["Anna", "Ben", "Clara"]:
        participant_service.add_participant(session, trip.id, n)

    # Anna pays 120 for all (each owes 40)
    expense_service.add_expense(
        session, trip.id, "Anna", Decimal("120"), "Dinner"
    )
    # Ben pays 30 for Ben+Clara (each owes 15)
    expense_service.add_expense(
        session, trip.id, "Ben", Decimal("30"), "Taxi", ["Ben", "Clara"]
    )

    transfers = calculate_settlements(session, trip.id)
    # Anna: paid 120, owes 40+0 = 40, balance = +80
    # Ben: paid 30, owes 40+15 = 55, balance = -25
    # Clara: paid 0, owes 40+15 = 55, balance = -55
    assert len(transfers) >= 1
    total = sum(t.amount for t in transfers)
    assert total == Decimal("80")
