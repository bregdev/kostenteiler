"""Tests for trip service."""

import pytest
from sqlalchemy.orm import Session

from src.services import trip_service


def test_create_trip(session: Session) -> None:
    trip = trip_service.create_trip(session, "Weekend Bern", "Fun trip")
    assert trip.id is not None
    assert trip.name == "Weekend Bern"
    assert trip.description == "Fun trip"
    assert trip.is_open is True


def test_list_trips(session: Session) -> None:
    trip_service.create_trip(session, "Trip A")
    trip_service.create_trip(session, "Trip B")
    trips = trip_service.list_trips(session)
    assert len(trips) == 2


def test_close_trip(session: Session) -> None:
    trip = trip_service.create_trip(session, "Trip")
    closed = trip_service.close_trip(session, trip.id)
    assert closed.is_open is False


def test_close_already_closed(session: Session) -> None:
    trip = trip_service.create_trip(session, "Trip")
    trip_service.close_trip(session, trip.id)
    with pytest.raises(ValueError, match="already closed"):
        trip_service.close_trip(session, trip.id)


def test_delete_trip(session: Session) -> None:
    trip = trip_service.create_trip(session, "Trip")
    name = trip_service.delete_trip(session, trip.id)
    assert name == "Trip"
    assert trip_service.get_trip(session, trip.id) is None


def test_delete_nonexistent(session: Session) -> None:
    with pytest.raises(ValueError, match="not found"):
        trip_service.delete_trip(session, 999)
