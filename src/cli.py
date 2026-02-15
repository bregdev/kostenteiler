"""CLI entry point using Click."""

from decimal import Decimal, InvalidOperation

import click

from src.db import Base, engine, get_session
from src.services import trip_service, participant_service, expense_service
from src.services.settlement_service import calculate_settlements
from src.services.export_service import export_trip_csv


@click.group()
def cli() -> None:
    """Kostenteiler -- split expenses fairly."""
    pass


# --- Trip commands ---


@cli.group()
def trip() -> None:
    """Manage trips."""
    pass


@trip.command("create")
@click.argument("name")
@click.option("--description", "-d", default=None, help="Optional description.")
def trip_create(name: str, description: str | None) -> None:
    """Create a new trip."""
    with get_session() as session:
        t = trip_service.create_trip(session, name, description)
        click.echo(f"Trip #{t.id} '{t.name}' created.")


@trip.command("list")
def trip_list() -> None:
    """List all trips."""
    with get_session() as session:
        trips = trip_service.list_trips(session)
        if not trips:
            click.echo("No trips yet.")
            return
        for t in trips:
            status = "open" if t.is_open else "closed"
            click.echo(f"  #{t.id}  {t.name} [{status}]")


@trip.command("show")
@click.argument("trip_id", type=int)
def trip_show(trip_id: int) -> None:
    """Show trip details."""
    with get_session() as session:
        t = trip_service.get_trip(session, trip_id)
        if not t:
            click.echo(f"Trip {trip_id} not found.")
            return
        status = "open" if t.is_open else f"closed ({t.closed_at:%Y-%m-%d})"
        click.echo(f"Trip #{t.id}: {t.name} [{status}]")
        if t.description:
            click.echo(f"  {t.description}")
        click.echo(f"  Participants: {len(t.participants)}")
        click.echo(f"  Expenses: {len(t.expenses)}")


@trip.command("close")
@click.argument("trip_id", type=int)
def trip_close(trip_id: int) -> None:
    """Close a trip."""
    with get_session() as session:
        try:
            t = trip_service.close_trip(session, trip_id)
            click.echo(f"Trip '{t.name}' closed.")
        except ValueError as e:
            click.echo(f"Error: {e}")


@trip.command("delete")
@click.argument("trip_id", type=int)
@click.confirmation_option(prompt="Are you sure you want to delete this trip?")
def trip_delete(trip_id: int) -> None:
    """Delete a trip and all its data."""
    with get_session() as session:
        try:
            name = trip_service.delete_trip(session, trip_id)
            click.echo(f"Trip '{name}' deleted.")
        except ValueError as e:
            click.echo(f"Error: {e}")


# --- Participant commands ---


@cli.group()
def participant() -> None:
    """Manage participants."""
    pass


@participant.command("add")
@click.argument("trip_id", type=int)
@click.argument("name")
def participant_add(trip_id: int, name: str) -> None:
    """Add a participant to a trip."""
    with get_session() as session:
        try:
            p = participant_service.add_participant(session, trip_id, name)
            click.echo(f"Added '{p.name}' to trip #{trip_id}.")
        except ValueError as e:
            click.echo(f"Error: {e}")


@participant.command("list")
@click.argument("trip_id", type=int)
def participant_list(trip_id: int) -> None:
    """List participants of a trip."""
    with get_session() as session:
        parts = participant_service.list_participants(session, trip_id)
        if not parts:
            click.echo("No participants yet.")
            return
        for p in parts:
            click.echo(f"  - {p.name}")


# --- Expense commands ---


@cli.group()
def expense() -> None:
    """Manage expenses."""
    pass


@expense.command("add")
@click.argument("trip_id", type=int)
@click.option("--paid-by", required=True, help="Name of the paying participant.")
@click.option("--amount", required=True, type=str, help="Amount in CHF.")
@click.option("--description", "-d", required=True, help="What the expense is for.")
@click.option("--for", "for_names", default=None, help='Comma-separated names, or omit for "all".')
def expense_add(
    trip_id: int, paid_by: str, amount: str, description: str, for_names: str | None
) -> None:
    """Add an expense to a trip."""
    try:
        amt = Decimal(amount)
    except InvalidOperation:
        click.echo(f"Error: '{amount}' is not a valid amount.")
        return

    names = [n.strip() for n in for_names.split(",")] if for_names else None

    with get_session() as session:
        try:
            exp = expense_service.add_expense(
                session, trip_id, paid_by, amt, description, names
            )
            split_info = ", ".join(s.participant.name for s in exp.splits)
            click.echo(
                f"Expense #{exp.id}: {exp.description} ({exp.amount:.2f} CHF) "
                f"paid by {paid_by}, split among [{split_info}]."
            )
        except ValueError as e:
            click.echo(f"Error: {e}")


@expense.command("list")
@click.argument("trip_id", type=int)
def expense_list(trip_id: int) -> None:
    """List all expenses for a trip."""
    with get_session() as session:
        expenses = expense_service.list_expenses(session, trip_id)
        if not expenses:
            click.echo("No expenses yet.")
            return
        for exp in expenses:
            split_names = ", ".join(s.participant.name for s in exp.splits)
            click.echo(
                f"  #{exp.id}  {exp.description}: {exp.amount:.2f} CHF "
                f"(paid by {exp.paid_by_participant.name}, for: {split_names})"
            )


@expense.command("edit")
@click.argument("expense_id", type=int)
@click.option("--amount", type=str, default=None, help="New amount.")
@click.option("--description", "-d", default=None, help="New description.")
def expense_edit(expense_id: int, amount: str | None, description: str | None) -> None:
    """Edit an existing expense."""
    amt = None
    if amount:
        try:
            amt = Decimal(amount)
        except InvalidOperation:
            click.echo(f"Error: '{amount}' is not a valid amount.")
            return

    with get_session() as session:
        try:
            exp = expense_service.edit_expense(session, expense_id, amt, description)
            click.echo(f"Expense #{exp.id} updated: {exp.description} ({exp.amount:.2f} CHF).")
        except ValueError as e:
            click.echo(f"Error: {e}")


@expense.command("delete")
@click.argument("expense_id", type=int)
@click.confirmation_option(prompt="Delete this expense?")
def expense_delete(expense_id: int) -> None:
    """Delete an expense."""
    with get_session() as session:
        try:
            desc = expense_service.delete_expense(session, expense_id)
            click.echo(f"Expense '{desc}' deleted.")
        except ValueError as e:
            click.echo(f"Error: {e}")


# --- Settle & Export ---


@cli.command()
@click.argument("trip_id", type=int)
def settle(trip_id: int) -> None:
    """Show settlement for a trip."""
    with get_session() as session:
        transfers = calculate_settlements(session, trip_id)
        if not transfers:
            click.echo("All settled -- no transfers needed.")
            return
        click.echo("Settlements:")
        for t in transfers:
            click.echo(f"  {t.from_name} -> {t.to_name}: {t.amount:.2f} CHF")


@cli.command()
@click.argument("trip_id", type=int)
@click.option("--output", "-o", default=None, help="Output CSV path.")
def export(trip_id: int, output: str | None) -> None:
    """Export trip to CSV."""
    with get_session() as session:
        t = trip_service.get_trip(session, trip_id)
        if not t:
            click.echo(f"Trip {trip_id} not found.")
            return
        path = output or f"trip_{trip_id}_{t.name.replace(' ', '_')}.csv"
        result = export_trip_csv(session, trip_id, path)
        click.echo(f"Exported to {result}")


def init_db() -> None:
    """Create all tables."""
    Base.metadata.create_all(engine)


if __name__ == "__main__":
    cli()
