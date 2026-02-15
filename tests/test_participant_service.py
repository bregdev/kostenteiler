"""Tests for participant service."""

import pytest
from sqlalchemy.orm import Session

from src.services import trip_service, participant_service


def test_add_participant(session: Session) -> None:
    trip = trip_service.create_trip(session, "Trip")
    p = participant_service.add_participant(session, trip.id, "Anna")
    assert p.name == "Anna"
    assert p.trip_id == trip.id


def test_duplicate_name(session: Session) -> None:
    trip = trip_service.create_trip(session, "Trip")
    participant_service.add_participant(session, trip.id, "Anna")
    with pytest.raises(ValueError, match="already exists"):
        participant_service.add_participant(session, trip.id, "Anna")


def test_max_participants(session: Session) -> None:
    trip = trip_service.create_trip(session, "Trip")
    for i in range(10):
        participant_service.add_participant(session, trip.id, f"Person{i}")
    with pytest.raises(ValueError, match="Maximum"):
        participant_service.add_participant(session, trip.id, "OneMore")


def test_add_to_closed_trip(session: Session) -> None:
    trip = trip_service.create_trip(session, "Trip")
    trip_service.close_trip(session, trip.id)
    with pytest.raises(ValueError, match="closed"):
        participant_service.add_participant(session, trip.id, "Anna")


def test_list_participants(session: Session) -> None:
    trip = trip_service.create_trip(session, "Trip")
    participant_service.add_participant(session, trip.id, "Ben")
    participant_service.add_participant(session, trip.id, "Anna")
    parts = participant_service.list_participants(session, trip.id)
    assert len(parts) == 2
    assert parts[0].name == "Anna"  # sorted
