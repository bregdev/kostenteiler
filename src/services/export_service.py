"""CSV export service."""

import csv
import io
from pathlib import Path

from sqlalchemy.orm import Session

from src.services.expense_service import list_expenses
from src.services.settlement_service import calculate_settlements


def export_trip_csv(
    session: Session, trip_id: int, output_path: str
) -> str:
    """Export trip expenses and settlements to CSV.

    Args:
        session: DB session.
        trip_id: Trip ID.
        output_path: File path for the CSV.

    Returns:
        The absolute path of the written file.
    """
    expenses = list_expenses(session, trip_id)
    settlements = calculate_settlements(session, trip_id)

    path = Path(output_path)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        # Expenses section
        writer.writerow(["=== Expenses ==="])
        writer.writerow(["ID", "Description", "Amount (CHF)", "Paid by", "Split among", "Date"])
        for exp in expenses:
            split_names = ", ".join(s.participant.name for s in exp.splits)
            writer.writerow([
                exp.id,
                exp.description,
                f"{exp.amount:.2f}",
                exp.paid_by_participant.name,
                split_names,
                exp.created_at.strftime("%Y-%m-%d %H:%M"),
            ])

        writer.writerow([])

        # Settlement section
        writer.writerow(["=== Settlements ==="])
        writer.writerow(["From", "To", "Amount (CHF)"])
        for t in settlements:
            writer.writerow([t.from_name, t.to_name, f"{t.amount:.2f}"])

    return str(path.resolve())
