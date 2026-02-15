# Konzept -- Kostenteiler

## Idee

CLI-basierte App zum Aufteilen von Kosten innerhalb einer Gruppe (max. 10 Personen).
Typischer Anwendungsfall: Wochenendtrip mit Freunden -- jeder zahlt verschiedene Dinge,
am Ende wird fair abgerechnet.

## User-Flow

### 1. Trip erstellen
- User startet die CLI und erstellt einen neuen Trip (Name, Datum/Zeitraum)
- Ein Trip ist die übergeordnete Einheit, die alle Ausgaben bündelt

### 2. Teilnehmer hinzufügen
- Dem Trip werden Teilnehmer hinzugefügt (Name, max. 10)
- Teilnehmer können nachträglich ergänzt werden (solange der Trip nicht abgeschlossen ist)

### 3. Ausgaben erfassen
- Jeder Teilnehmer kann beliebig viele Ausgaben hinzufügen
- Pro Ausgabe: Beschreibung, Betrag, wer hat bezahlt, für wen (alle oder Subset)
- Aufteilung immer gleichmässig (Betrag / Anzahl Beteiligte)
- Ausgaben können bearbeitet und gelöscht werden (solange Trip offen)
- Beispiel: "Abendessen 120 CHF, bezahlt von Anna, für alle"
- Beispiel: "Taxi 30 CHF, bezahlt von Ben, für Ben und Clara"

### 4. Abrechnung anzeigen
- Übersicht aller Ausgaben pro Trip
- Berechnung: Wer schuldet wem wie viel?
- Minimierung der Transaktionen (nicht jeder zahlt jedem, sondern optimierte Transfers)
- Ausgabe als Tabelle in der CLI

### 5. Trip abschliessen
- Trip kann als "abgeschlossen" markiert werden
- Abgeschlossene Trips können noch angezeigt, aber nicht mehr bearbeitet werden

### 6. Trip löschen
- Offene und abgeschlossene Trips können gelöscht werden
- Cascade: löscht alle zugehörigen Participants, Expenses und Splits

### 7. Trip-Übersicht
- Alle Trips auflisten (offen / abgeschlossen)
- Einzelnen Trip mit Details anzeigen

### 8. CSV-Export
- Export aller Ausgaben eines Trips als CSV
- Enthält: Beschreibung, Betrag, bezahlt von, aufgeteilt auf, Datum
- Zusätzlich: Settlement-Transfers (wer zahlt wem wie viel)

## Datenmodell

### Trip
- id (PK)
- name
- description (optional)
- created_at
- closed_at (nullable -- null = offen)

### Participant
- id (PK)
- trip_id (FK -> Trip)
- name

### Expense
- id (PK)
- trip_id (FK -> Trip)
- paid_by (FK -> Participant)
- description
- amount (Decimal)
- created_at

### ExpenseSplit
- id (PK)
- expense_id (FK -> Expense)
- participant_id (FK -> Participant)
- share_amount (Decimal)

## Abrechnungs-Algorithmus

1. Pro Participant: Summe aller Zahlungen vs. Summe aller Anteile berechnen
2. Saldo pro Person = bezahlt - geschuldet
3. Alle Beträge auf 5 Rappen runden (CH-Standard)
4. Positive Salden = bekommen Geld, negative = schulden Geld
5. Greedy-Algorithmus zur Minimierung der Transaktionen:
   - Grösster Schuldner zahlt an grössten Gläubiger
   - Wiederholen bis alle Salden ausgeglichen

### Rundung auf 5 Rappen
- `round_to_05(amount)`: Rundet auf nächste 0.05 CHF
- Beispiel: 33.33 -> 33.35, 33.37 -> 33.35, 33.38 -> 33.40
- Wird bei der Berechnung der Splits und der finalen Settlements angewendet

## Datenbank

### Entscheid: PostgreSQL (lokal)
- Wie vom User gewünscht: lokale PostgreSQL-Instanz
- Verbindung via `psycopg2` (oder `psycopg[binary]` für einfacheres Setup)
- DB-Name: `kostenteiler`
- Setup: User muss lokale PostgreSQL-Instanz laufen haben
- Migrations: `alembic` für Schema-Migrationen

### Lokales DB-Setup
```bash
# PostgreSQL muss lokal installiert sein (z.B. via Homebrew)
brew install postgresql@17
brew services start postgresql@17

# Datenbank erstellen
createdb kostenteiler
```

### Verbindung
- Connection-String via `.env`: `DATABASE_URL=postgresql://localhost:5432/kostenteiler`
- SQLAlchemy als ORM

## CLI-Struktur (geplant)

```
kostenteiler trip create "Wochenende Bern"
kostenteiler trip list
kostenteiler trip show <trip-id>
kostenteiler trip close <trip-id>

kostenteiler participant add <trip-id> "Anna"
kostenteiler participant list <trip-id>

kostenteiler expense add <trip-id> --paid-by "Anna" --amount 120 --description "Abendessen" --for all
kostenteiler expense add <trip-id> --paid-by "Ben" --amount 30 --description "Taxi" --for "Ben,Clara"
kostenteiler expense list <trip-id>

kostenteiler expense edit <expense-id> --amount 150 --description "Abendessen für alle"
kostenteiler expense delete <expense-id>

kostenteiler settle <trip-id>
kostenteiler export <trip-id> --output "trip_bern.csv"

kostenteiler trip delete <trip-id>
```

## Tech Stack (Entscheid)

| Bereich | Wahl | Begründung |
|---------|------|------------|
| CLI-Framework | Click | Mächtiger als argparse, guter Subcommand-Support, weit verbreitet |
| ORM | SQLAlchemy 2.0 | Standard in Python, guter PostgreSQL-Support, Type-Hint-kompatibel |
| Migrationen | Alembic | Native SQLAlchemy-Integration |
| DB-Adapter | psycopg2-binary | Stabil, kein Build-Tooling nötig |
| Config | python-dotenv | Einfach, .env-Datei reicht |
| Testing | pytest + pytest-cov | Standard, 80% Coverage Minimum |
| Formatting | Black | Wie vom User gewünscht |

## Projektstruktur

- `src/cli.py` -- Click Entry-Point mit Subcommands (trip, participant, expense, settle)
- `src/db.py` -- Engine, Session-Factory, Base
- `src/models/` -- SQLAlchemy Models (Trip, Participant, Expense, ExpenseSplit)
- `src/services/` -- Business-Logik pro Entität + Settlement-Algorithmus
- `tests/` -- pytest Tests, ein File pro Service

## Entschiedene Design-Fragen

- [x] **Währung**: Fix CHF, nicht konfigurierbar
- [x] **Aufteilung**: Nur gleichmässig aufteilen (Betrag / Anzahl Beteiligte)
- [x] **Rundung**: Auf 5 Rappen runden (CH-typisch, `round_to_05()`)
- [x] **CSV-Export**: Ja -- alle Ausgaben + Settlement-Transfers in einer Datei
- [x] **Trips löschen**: Ja, Trips können gelöscht werden (Cascade löscht Participants, Expenses, Splits)
- [x] **Ausgaben bearbeiten/löschen**: Ja, solange Trip offen ist
- [x] **Teilnehmer-Referenz in CLI**: Per Name (muss pro Trip eindeutig sein)

## Noch nicht im Scope

- Web-UI / API (erstmal nur CLI)
- Multi-User / Authentication
- Cloud-Deployment
