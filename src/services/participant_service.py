"""Participant service for CRUD operations."""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models import Participant, Trip


def add_participant(session: Session, trip_id: int, name: str) -> Participant:
    """Add a participant to a trip. Raises ValueError on issues."""
    trip = session.get(Trip, trip_id)
    if not trip:
        raise ValueError(f"Trip {trip_id} not found.")
    if not trip.is_open:
        raise ValueError(f"Trip '{trip.name}' is closed.")
    if len(trip.participants) >= 10:
        raise ValueError("Maximum of 10 participants per trip.")

    existing = session.execute(
        select(Participant).where(
            Participant.trip_id == trip_id, Participant.name == name
        )
    ).scalar_one_or_none()
    if existing:
        raise ValueError(f"Participant '{name}' already exists in this trip.")

    participant = Participant(trip_id=trip_id, name=name)
    session.add(participant)
    session.commit()
    session.refresh(participant)
    return participant


def list_participants(session: Session, trip_id: int) -> list[Participant]:
    """Return all participants of a trip."""
    return list(
        session.execute(
            select(Participant)
            .where(Participant.trip_id == trip_id)
            .order_by(Participant.name)
        ).scalars()
    )


def get_participant_by_name(
    session: Session, trip_id: int, name: str
) -> Optional[Participant]:
    """Find a participant by name within a trip."""
    return session.execute(
        select(Participant).where(
            Participant.trip_id == trip_id, Participant.name == name
        )
    ).scalar_one_or_none()
