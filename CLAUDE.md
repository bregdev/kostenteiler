# CLAUDE.md

## Projekt

Kostenteiler -- Python-Projekt (Python 3.13).

## Projektbeschreibung
- CLI-basierter Kostenteiler für bis zu 10 Personen
- Anwendungsfall: Wochenendtrip mit Freunden -- jeder hat individuelle Ausgaben, am Ende wird fair aufgeteilt
- Detailliertes Konzept und Design-Entscheide: siehe **Konzept.md**

### User-Flow (Kurzfassung)
1. **Trip erstellen** -- neuer Trip mit Name und optionaler Beschreibung
2. **Teilnehmer hinzufügen** -- bis zu 10 Personen pro Trip, referenziert per Name (eindeutig pro Trip)
3. **Ausgaben erfassen** -- wer hat bezahlt, wie viel, für wen (alle oder Subset), gleichmässig aufgeteilt
4. **Ausgaben bearbeiten/löschen** -- solange Trip offen ist
5. **Abrechnung** -- optimierte Berechnung wer wem wie viel schuldet (minimale Transaktionen)
6. **CSV-Export** -- alle Ausgaben + Settlement-Transfers
7. **Trip abschliessen** -- danach nur noch lesbar
8. **Trip löschen** -- mit Cascade auf alle zugehörigen Daten

### Geschäftsregeln
- Währung: **nur CHF**
- Aufteilung: **immer gleichmässig** (Betrag / Anzahl Beteiligte)
- Rundung: **auf 5 Rappen** (CH-Standard)

### Datenbank
- **PostgreSQL** (lokale Instanz)
- Connection-String via `.env`: `DATABASE_URL=postgresql://localhost:5432/kostenteiler`
- ORM: **SQLAlchemy 2.0**
- Migrationen: **Alembic**

## Tech Stack
- Python 3.13
- **Click** (CLI-Framework)
- **SQLAlchemy 2.0** (ORM) + **Alembic** (Migrationen)
- **psycopg2-binary** (PostgreSQL-Adapter)
- **python-dotenv** (Umgebungsvariablen)
- **pytest** für Testing
- **Black** für Formatting

## Umgebung

- Virtual Environment: `.venv/` (aktivieren mit `source .venv/bin/activate`)
- Abhängigkeiten installieren: `pip install -r requirements.txt`
- Dev-Abhängigkeiten installieren: `pip install -r requirements-dev.txt`

## Code-Stil

- Formatter: **Black** (Standardkonfiguration, Line Length 88)
- Alle Funktionen und Methoden brauchen **Type Hints** (Parameter + Return Type)
- Alle öffentlichen Funktionen, Klassen und Module brauchen **Docstrings** (Google-Style)
- Sprache im Code (Variablen, Docstrings, Kommentare): Englisch

## Standards
- Type Hints in allen Funktionen
- Docstrings nach Google-Style
- PEP 8 Formatting (ruff oder black)
- 80% Test-Coverage minimum

## Testing

- Framework: **pytest**
- Tests ausführen: `pytest`
- Tests liegen in `tests/` und spiegeln die Struktur von `src/`
- Testdateien heissen `test_<modul>.py`

## Git

- Commits werden **manuell** vom User gemacht -- niemals automatisch committen
- Keine Commits erstellen, es sei denn der User fragt explizit danach
- Commit Kommentare auf englisch, lowercase vorschlagen
- Commit Messages nach Conventional Commits
- Neue Features in Feature-Branches

## Workflow

- Der User reviewt Code in **VS Code**
- Keine Dateien pushen ohne explizite Aufforderung
- Vor Code-Änderungen immer zuerst die betroffenen Dateien lesen

## Security
- Keine API-Keys oder Secrets im Code
- Sensitive Config in .env (not in Git)
- Input Validation für alle User-Inputs

# Development Constraints

- Alle Python-Dependencies via pip in `.venv` installieren
- Keine System-weiten Installationen
- Nur Dependencies von PyPI oder GitHub (keine unbekannten Quellen)
- Vor Installation neuer Dependencies: Liste zeigen und Bestätigung einholen

## Projekt Struktur
```
kostenteiler/
├── CLAUDE.md
├── Konzept.md
├── requirements.txt
├── requirements-dev.txt
├── .env                     # DATABASE_URL etc. (nicht in Git)
├── .gitignore
├── alembic.ini
├── alembic/
│   ├── env.py
│   └── versions/
├── src/
│   ├── __init__.py
│   ├── cli.py               # Click CLI entry point
│   ├── db.py                # SQLAlchemy engine & session
│   ├── models/
│   │   ├── __init__.py
│   │   ├── trip.py           # Trip model
│   │   ├── participant.py    # Participant model
│   │   └── expense.py        # Expense + ExpenseSplit models
│   └── services/
│       ├── __init__.py
│       ├── trip_service.py
│       ├── participant_service.py
│       ├── expense_service.py
│       ├── settlement_service.py  # Abrechnungs-Algorithmus
│       └── export_service.py      # CSV-Export
└── tests/
    ├── __init__.py
    ├── conftest.py           # Fixtures (test DB, sessions)
    ├── test_trip_service.py
    ├── test_participant_service.py
    ├── test_expense_service.py
    └── test_settlement_service.py
```

## Constraints
- Nur Dependencies aus requirements.txt
- Keine Breaking Changes ohne Diskussion
- Tests vor jeder Implementation
