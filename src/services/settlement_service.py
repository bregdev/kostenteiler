"""Settlement service -- calculates who owes whom."""

from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models import Expense, ExpenseSplit, Participant
from src.services.expense_service import round_to_05


@dataclass
class Transfer:
    """A single transfer from debtor to creditor."""

    from_name: str
    to_name: str
    amount: Decimal


def calculate_settlements(
    session: Session, trip_id: int
) -> list[Transfer]:
    """Calculate minimal transfers to settle all debts for a trip.

    Returns:
        List of Transfer objects representing who pays whom.
    """
    participants = list(
        session.execute(
            select(Participant).where(Participant.trip_id == trip_id)
        ).scalars()
    )

    if not participants:
        return []

    balances: dict[str, Decimal] = {p.name: Decimal("0") for p in participants}

    expenses = list(
        session.execute(
            select(Expense).where(Expense.trip_id == trip_id)
        ).scalars()
    )

    for expense in expenses:
        payer_name = expense.paid_by_participant.name
        balances[payer_name] += expense.amount

        splits = list(
            session.execute(
                select(ExpenseSplit).where(ExpenseSplit.expense_id == expense.id)
            ).scalars()
        )
        for split in splits:
            balances[split.participant.name] -= split.share_amount

    # Round balances to 0.05
    balances = {name: round_to_05(bal) for name, bal in balances.items()}

    return _minimize_transfers(balances)


def _minimize_transfers(balances: dict[str, Decimal]) -> list[Transfer]:
    """Greedy algorithm to minimize number of transfers."""
    debtors = sorted(
        [(name, -bal) for name, bal in balances.items() if bal < 0],
        key=lambda x: x[1],
        reverse=True,
    )
    creditors = sorted(
        [(name, bal) for name, bal in balances.items() if bal > 0],
        key=lambda x: x[1],
        reverse=True,
    )

    transfers: list[Transfer] = []
    i, j = 0, 0

    while i < len(debtors) and j < len(creditors):
        debtor_name, debt = debtors[i]
        creditor_name, credit = creditors[j]

        amount = min(debt, credit)
        amount = round_to_05(amount)

        if amount > 0:
            transfers.append(Transfer(
                from_name=debtor_name,
                to_name=creditor_name,
                amount=amount,
            ))

        debtors[i] = (debtor_name, debt - amount)
        creditors[j] = (creditor_name, credit - amount)

        if debtors[i][1] <= 0:
            i += 1
        if creditors[j][1] <= 0:
            j += 1

    return transfers
