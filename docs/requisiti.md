# Documento dei requisiti — Biobank Tracker

**Versione documento:** 1.0  **Stato:** approvato per la release 1.0.0

## 1. Scopo
Software da riga di comando per registrare campioni biologici, conoscerne
posizione e stato, e conservare uno storico non alterabile di ogni operazione.

## 2. Utenti
Tecnico di biobanca che gestisce l'inventario dei campioni.

## 3. Requisiti funzionali

| ID | Requisito |
|---|---|
| REQ-01 | Il sistema deve permettere di registrare un campione con ID, tipo, data di prelievo e posizione; lo stato iniziale è `in_storage`. |
| REQ-02 | Il sistema deve rifiutare la registrazione di un ID già esistente. |
| REQ-03 | Il sistema deve rifiutare dati non validi: ID o posizione vuoti, tipo non ammesso, data non valida o futura. In caso di rifiuto nulla viene salvato. |
| REQ-04 | Il sistema deve permettere di consultare un campione tramite ID e segnalare chiaramente se non esiste. |
| REQ-05 | Il sistema deve permettere di elencare i campioni, filtrando per tipo e/o stato. |
| REQ-06 | Il sistema deve permettere di spostare un campione in una nuova posizione, registrando lo spostamento. |
| REQ-07 | Il sistema deve permettere di cambiare lo stato di un campione (`in_storage`, `in_use`, `consumed`, `discarded`). Gli stati `consumed` e `discarded` sono finali: il campione non può più cambiare stato né essere spostato. |
| REQ-08 | Il sistema deve registrare ogni operazione (registrazione, spostamento, cambio stato) in uno storico con data e ora UTC; lo storico non può essere modificato né cancellato ed è consultabile per campione. |

## 4. Requisiti non funzionali

| ID | Requisito |
|---|---|
| REQ-09 | I dati devono persistere tra un'esecuzione e l'altra (SQLite). |
| REQ-10 | Il sistema deve essere utilizzabile da riga di comando; in caso di errore deve restituire un messaggio leggibile e un codice di uscita diverso da 0. |

## 5. Tipi di campione ammessi
`blood`, `plasma`, `serum`, `tissue`, `dna`

## 6. Fuori ambito nella versione 1.0
Autenticazione utenti, interfaccia grafica, importazione/esportazione, gestione
di più biobanche.

## 7. Registro delle richieste di modifica
| ID | Descrizione | Stato |
|---|---|---|
| CR-01 | *(da compilare nel Giorno 2: es. impedire che due campioni attivi occupino la stessa posizione)* | Aperta |
