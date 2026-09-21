# Biobank Tracker

Software da riga di comando (Python + SQLite) per la gestione di campioni
biologici con storico delle operazioni non alterabile. Progetto didattico per
mostrare l'intero ciclo di vita del software: requisiti, progettazione,
implementazione, verifica, rilascio e manutenzione.

## Installazione
```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
```

## Uso
```bash
python -m biobank add S001 blood 2024-05-10 F1-R2-B3
python -m biobank list --type blood
python -m biobank move S001 F2-R1-B1
python -m biobank status S001 in_use
python -m biobank history S001
```
Il database è il file `biobank.db` (opzione `--db` per cambiarlo).

## Test
```bash
pytest
```

## Documentazione
- [Requisiti](docs/requisiti.md)
- [Matrice di tracciabilità](docs/tracciabilita.md)
- [Changelog](CHANGELOG.md)

## Ciclo di vita seguito
| Fase | Artefatto |
|---|---|
| Requisiti | `docs/requisiti.md` |
| Progettazione | *(da aggiungere: `docs/progettazione.md`)* |
| Implementazione | `biobank/` (cronologia Git) |
| Verifica | `tests/` + `docs/tracciabilita.md` |
| Rilascio | tag Git `v1.0.0`, `CHANGELOG.md` |
| Manutenzione | CR-01 → versione 1.1.0 |
