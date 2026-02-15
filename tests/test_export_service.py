"""Tests for CSV export service."""

import csv
import tempfile
from decimal import Decimal
from pathlib import Path

from sqlalchemy.orm import Session

from src.services import trip_service, participant_service, expense_service
from src.services.export_service import export_trip_csv


def test_export_csv(session: Session) -> None:
    trip = trip_service.create_trip(session, "Trip")
    for n in ["Anna", "Ben", "Clara"]:
        participant_service.add_participant(session, trip.id, n)

    expense_service.add_expense(
        session, trip.id, "Anna", Decimal("90"), "Dinner"
    )
    expense_service.add_expense(
        session, trip.id, "Ben", Decimal("30"), "Taxi", ["Ben", "Clara"]
    )

    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
        path = f.name

    result = export_trip_csv(session, trip.id, path)
    content = Path(result).read_text()

    assert "Dinner" in content
    assert "Taxi" in content
    assert "=== Settlements ===" in content
    assert "Anna" in content

    # Verify it's valid CSV
    with open(result) as f:
        reader = csv.reader(f)
        rows = list(reader)
    assert len(rows) >= 5  # headers + 2 expenses + blank + settlement header + transfers

    Path(result).unlink()
