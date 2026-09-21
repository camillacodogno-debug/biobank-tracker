"""Test di verifica. Il nome di ogni test indica il requisito verificato."""
import sqlite3
from datetime import date, timedelta

import pytest

from biobank.cli import main
from biobank.db import connect
from biobank.service import (
    DuplicateSampleError, InvalidOperationError, SampleNotFoundError,
    SampleService, ValidationError,
)


@pytest.fixture
def service():
    conn = connect(":memory:")
    yield SampleService(conn)
    conn.close()


def _add(service, sample_id="S001", sample_type="blood",
         collection_date="2024-05-10", location="F1-R2-B3"):
    return service.register(sample_id, sample_type, collection_date, location)


def test_req01_register_sample(service):
    s = _add(service)
    assert s["sample_id"] == "S001"
    assert s["status"] == "in_storage"
    assert s["location"] == "F1-R2-B3"


def test_req02_duplicate_id_rejected(service):
    _add(service)
    with pytest.raises(DuplicateSampleError):
        _add(service)


@pytest.mark.parametrize("kwargs", [
    {"sample_id": "  "},
    {"sample_type": "urine"},
    {"collection_date": "10/05/2024"},
    {"collection_date": (date.today() + timedelta(days=1)).isoformat()},
    {"location": ""},
])
def test_req03_invalid_input_rejected(service, kwargs):
    with pytest.raises(ValidationError):
        _add(service, **kwargs)
    assert service.search() == []  # nulla è stato salvato


def test_req04_get_by_id(service):
    _add(service)
    assert service.get("S001")["sample_type"] == "blood"
    with pytest.raises(SampleNotFoundError):
        service.get("NOPE")


def test_req05_search_filters(service):
    _add(service, "S001", "blood")
    _add(service, "S002", "dna")
    service.set_status("S002", "in_use")
    assert [s["sample_id"] for s in service.search()] == ["S001", "S002"]
    assert [s["sample_id"] for s in service.search(sample_type="dna")] == ["S002"]
    assert [s["sample_id"] for s in service.search(status="in_use")] == ["S002"]


def test_req06_move_updates_location_and_is_logged(service):
    _add(service)
    service.move("S001", "F2-R1-B1")
    assert service.get("S001")["location"] == "F2-R1-B1"
    assert service.history("S001")[-1]["action"] == "MOVED"
    with pytest.raises(InvalidOperationError):  # stessa posizione
        service.move("S001", "F2-R1-B1")


def test_req07_status_change_and_final_states(service):
    _add(service)
    service.set_status("S001", "consumed")
    with pytest.raises(InvalidOperationError):
        service.set_status("S001", "in_storage")
    with pytest.raises(InvalidOperationError):
        service.move("S001", "F9-R9-B9")


def test_req07_invalid_status_rejected(service):
    _add(service)
    with pytest.raises(ValidationError):
        service.set_status("S001", "lost")


def test_req08_history_is_ordered_and_complete(service):
    _add(service)
    service.move("S001", "F2-R1-B1")
    service.set_status("S001", "in_use")
    actions = [e["action"] for e in service.history("S001")]
    assert actions == ["REGISTERED", "MOVED", "STATUS_CHANGED"]


def test_req08_audit_log_is_append_only(service):
    _add(service)
    with pytest.raises(sqlite3.DatabaseError):
        service.conn.execute("UPDATE audit_log SET action = 'X'")
    with pytest.raises(sqlite3.DatabaseError):
        service.conn.execute("DELETE FROM audit_log")


def test_req09_data_persists_between_sessions(tmp_path):
    path = str(tmp_path / "test.db")
    conn = connect(path)
    SampleService(conn).register("S001", "tissue", "2024-01-02", "F1")
    conn.close()
    conn = connect(path)
    assert SampleService(conn).get("S001")["sample_type"] == "tissue"
    conn.close()


def test_req10_cli_end_to_end(tmp_path, capsys):
    db = str(tmp_path / "cli.db")
    assert main(["--db", db, "add", "S001", "blood", "2024-05-10", "F1"]) == 0
    assert main(["--db", db, "move", "S001", "F2"]) == 0
    assert main(["--db", db, "list", "--type", "blood"]) == 0
    out = capsys.readouterr().out
    assert "S001" in out and "F2" in out
    assert main(["--db", db, "show", "MISSING"]) == 1  # errore -> codice 1
