"""Persistenza su SQLite (REQ-09) e registro storico append-only (REQ-08)."""
import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS samples (
    sample_id       TEXT PRIMARY KEY,
    sample_type     TEXT NOT NULL,
    collection_date TEXT NOT NULL,
    location        TEXT NOT NULL,
    status          TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS audit_log (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    sample_id TEXT NOT NULL,
    action    TEXT NOT NULL,
    details   TEXT NOT NULL,
    timestamp TEXT NOT NULL
);

-- Il registro non può essere modificato né cancellato (REQ-08)
CREATE TRIGGER IF NOT EXISTS audit_no_update
BEFORE UPDATE ON audit_log
BEGIN SELECT RAISE(ABORT, 'audit_log is append-only'); END;

CREATE TRIGGER IF NOT EXISTS audit_no_delete
BEFORE DELETE ON audit_log
BEGIN SELECT RAISE(ABORT, 'audit_log is append-only'); END;
"""


def connect(path: str = "biobank.db") -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn
