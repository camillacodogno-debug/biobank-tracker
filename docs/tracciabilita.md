# Matrice di tracciabilità

Ogni requisito è collegato al codice che lo implementa e ai test che lo verificano.

| Requisito | Implementazione | Test di verifica |
|---|---|---|
| REQ-01 | `SampleService.register` | `test_req01_register_sample` |
| REQ-02 | `SampleService.register` | `test_req02_duplicate_id_rejected` |
| REQ-03 | `SampleService.register` | `test_req03_invalid_input_rejected` |
| REQ-04 | `SampleService.get` | `test_req04_get_by_id` |
| REQ-05 | `SampleService.search` | `test_req05_search_filters` |
| REQ-06 | `SampleService.move` | `test_req06_move_updates_location_and_is_logged` |
| REQ-07 | `SampleService.set_status` | `test_req07_status_change_and_final_states`, `test_req07_invalid_status_rejected` |
| REQ-08 | `SampleService._log`, trigger in `db.py` | `test_req08_history_is_ordered_and_complete`, `test_req08_audit_log_is_append_only` |
| REQ-09 | `db.connect` | `test_req09_data_persists_between_sessions` |
| REQ-10 | `cli.main` | `test_req10_cli_end_to_end` |
