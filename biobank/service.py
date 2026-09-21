"""Logica di business. Ogni metodo indica il requisito che implementa."""
import sqlite3
from datetime import date, datetime, timezone

SAMPLE_TYPES = {"blood", "plasma", "serum", "tissue", "dna"}
STATUSES = {"in_storage", "in_use", "consumed", "discarded"}
FINAL_STATUSES = {"consumed", "discarded"}


class BiobankError(Exception):
    """Errore base del dominio."""


class ValidationError(BiobankError):
    pass


class DuplicateSampleError(BiobankError):
    pass


class SampleNotFoundError(BiobankError):
    pass


class InvalidOperationError(BiobankError):
    pass


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class SampleService:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    # REQ-01, REQ-02, REQ-03
    def register(self, sample_id, sample_type, collection_date, location) -> dict:
        sample_id = (sample_id or "").strip()
        location = (location or "").strip()
        if not sample_id:
            raise ValidationError("L'ID del campione è obbligatorio")
        if not location:
            raise ValidationError("La posizione è obbligatoria")
        if sample_type not in SAMPLE_TYPES:
            raise ValidationError(
                f"Tipo non valido: usare uno tra {sorted(SAMPLE_TYPES)}"
            )
        try:
            collected = date.fromisoformat(collection_date)
        except (TypeError, ValueError):
            raise ValidationError("Data non valida: usare il formato AAAA-MM-GG")
        if collected > date.today():
            raise ValidationError("La data di prelievo non può essere futura")

        try:
            with self.conn:  # transazione: campione + log insieme, o niente
                self.conn.execute(
                    "INSERT INTO samples VALUES (?, ?, ?, ?, 'in_storage')",
                    (sample_id, sample_type, collected.isoformat(), location),
                )
                self._log(sample_id, "REGISTERED",
                          f"type={sample_type}; location={location}")
        except sqlite3.IntegrityError:
            raise DuplicateSampleError(f"Esiste già un campione con ID {sample_id}")
        return self.get(sample_id)

    # REQ-04
    def get(self, sample_id) -> dict:
        row = self.conn.execute(
            "SELECT * FROM samples WHERE sample_id = ?", (sample_id,)
        ).fetchone()
        if row is None:
            raise SampleNotFoundError(f"Campione {sample_id} non trovato")
        return dict(row)

    # REQ-05
    def search(self, sample_type=None, status=None) -> list[dict]:
        query, params = "SELECT * FROM samples WHERE 1=1", []
        if sample_type:
            query += " AND sample_type = ?"
            params.append(sample_type)
        if status:
            query += " AND status = ?"
            params.append(status)
        query += " ORDER BY sample_id"
        return [dict(r) for r in self.conn.execute(query, params)]

    # REQ-06
    def move(self, sample_id, new_location) -> dict:
        new_location = (new_location or "").strip()
        if not new_location:
            raise ValidationError("La nuova posizione è obbligatoria")
        sample = self.get(sample_id)
        if sample["status"] in FINAL_STATUSES:
            raise InvalidOperationError(
                f"Campione {sample['status']}: non può essere movimentato"
            )
        if sample["location"] == new_location:
            raise InvalidOperationError("Il campione è già in quella posizione")
        with self.conn:
            self.conn.execute(
                "UPDATE samples SET location = ? WHERE sample_id = ?",
                (new_location, sample_id),
            )
            self._log(sample_id, "MOVED",
                      f"from={sample['location']}; to={new_location}")
        return self.get(sample_id)

    # REQ-07
    def set_status(self, sample_id, new_status) -> dict:
        if new_status not in STATUSES:
            raise ValidationError(f"Stato non valido: usare uno tra {sorted(STATUSES)}")
        sample = self.get(sample_id)
        if sample["status"] in FINAL_STATUSES:
            raise InvalidOperationError(
                f"Stato finale ({sample['status']}): non può più cambiare"
            )
        if sample["status"] == new_status:
            raise InvalidOperationError("Il campione è già in questo stato")
        with self.conn:
            self.conn.execute(
                "UPDATE samples SET status = ? WHERE sample_id = ?",
                (new_status, sample_id),
            )
            self._log(sample_id, "STATUS_CHANGED",
                      f"from={sample['status']}; to={new_status}")
        return self.get(sample_id)

    # REQ-08
    def history(self, sample_id) -> list[dict]:
        self.get(sample_id)  # solleva errore se non esiste
        rows = self.conn.execute(
            "SELECT timestamp, action, details FROM audit_log "
            "WHERE sample_id = ? ORDER BY id",
            (sample_id,),
        )
        return [dict(r) for r in rows]

    def _log(self, sample_id, action, details):
        self.conn.execute(
            "INSERT INTO audit_log (sample_id, action, details, timestamp) "
            "VALUES (?, ?, ?, ?)",
            (sample_id, action, details, _now()),
        )
