# CLAUDE.md

## Projekt

Kostenteiler -- Python-Projekt (Python 3.13).

## Umgebung

- Virtual Environment: `.venv/` (aktivieren mit `source .venv/bin/activate`)
- Abhängigkeiten installieren: `pip install -r requirements.txt`
- Dev-Abhängigkeiten installieren: `pip install -r requirements-dev.txt`

## Code-Stil

- Formatter: **Black** (Standardkonfiguration, Line Length 88)
- Alle Funktionen und Methoden brauchen **Type Hints** (Parameter + Return Type)
- Alle öffentlichen Funktionen, Klassen und Module brauchen **Docstrings** (Google-Style)
- Sprache im Code (Variablen, Docstrings, Kommentare): Englisch

## Testing

- Framework: **pytest**
- Tests ausführen: `pytest`
- Tests liegen in `tests/` und spiegeln die Struktur von `src/`
- Testdateien heissen `test_<modul>.py`

## Git

- Commits werden **manuell** vom User gemacht -- niemals automatisch committen
- Keine Commits erstellen, es sei denn der User fragt explizit danach

## Workflow

- Der User reviewt Code in **VS Code**
- Keine Dateien pushen ohne explizite Aufforderung
- Vor Code-Änderungen immer zuerst die betroffenen Dateien lesen
