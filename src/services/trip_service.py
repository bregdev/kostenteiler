"""Trip service for CRUD operations."""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models import Trip


def create_trip(
    session: Session, name: str, description: Optional[str] = None
) -> Trip:
    """Create a new trip."""
    trip = Trip(name=name, description=description)
    session.add(trip)
    session.commit()
    session.refresh(trip)
    return trip


def list_trips(session: Session) -> list[Trip]:
    """Return all trips ordered by creation date."""
    return list(session.execute(select(Trip).order_by(Trip.created_at.desc())).scalars())


def get_trip(session: Session, trip_id: int) -> Optional[Trip]:
    """Return a trip by ID or None."""
    return session.get(Trip, trip_id)


def close_trip(session: Session, trip_id: int) -> Trip:
    """Close a trip. Raises ValueError if already closed."""
    trip = session.get(Trip, trip_id)
    if not trip:
        raise ValueError(f"Trip {trip_id} not found.")
    if not trip.is_open:
        raise ValueError(f"Trip '{trip.name}' is already closed.")
    trip.closed_at = datetime.now(timezone.utc)
    session.commit()
    session.refresh(trip)
    return trip


def delete_trip(session: Session, trip_id: int) -> str:
    """Delete a trip and all related data. Returns trip name."""
    trip = session.get(Trip, trip_id)
    if not trip:
        raise ValueError(f"Trip {trip_id} not found.")
    name = trip.name
    session.delete(trip)
    session.commit()
    return name
