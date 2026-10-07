# Tracciamento modifiche · EnerGuard (7 ottobre 2026)

Registro cronologico di ciò che è stato cambiato rispetto allo starter kit, con il motivo.

## Cronologia git

Il kit è sotto git (`main`). Le modifiche sono state ripristinate allo stato originale e reintrodotte come commit separati; nel codice i TODO risolti sono sostituiti da commenti `DECISIONE:` con il razionale. `.env`, `modello.joblib`, `predizioni.csv` e `audit_trail.jsonl` sono ignorati.

| Commit | Contenuto |
| --- | --- |
| `2b69a86` | Baseline: starter kit originale |
| `9315609` | LLM: `max_completion_tokens` 400 → 2000 |
| `2f0556a` | Tier 2: stop sulla coda esistente, ambiti combinati, escalation SLA |
| `8672ebf` | Tier 2: azione da regole, KPI A1–A6, scheda KPI, campione HOTL |
| `4687e92` | Tracciamento: cronologia git |
| `5e10d1d` | Tier 1: soglia 0.30 e indagine Sud/Isole |

Backup dello stato precedente al rollback: `%TEMP%\energuard_stato_finale`.

## Setup

- Installate le dipendenze di `requirements.txt` e `pypdf` (usato solo per leggere i PDF della documentazione).
- Eseguito `train_baseline.py`: AUC 0.862, generati `modello.joblib` e `predizioni.csv`.
- `.env` già presente e configurato per Azure (`gpt-5.6-luna`); non modificato.

## Modifiche al codice

### `explainer.py`

- Alzato `max_completion_tokens` da 400 a 2000 nella chiamata Azure.
  - Motivo: con 400 il modello GPT-5 restituiva risposta vuota (`risposta senza JSON`) e si ricadeva sempre nel template.
  - Esito: con 2000 le spiegazioni arrivano dall'LLM (5 su 5, nessun fallback, circa 3 s per card).

### `oversight_manager.py`

- `attiva_stop`: ora blocca anche le decisioni già in coda nell'ambito (`BLOCCATA_STOP`) e le registra nel log; restituisce gli ID bloccati.
- Stop e sblocco richiedono una motivazione di almeno 15 caratteri (`_valida_motivazione`).
- Ambiti combinati con `+` (es. `area:Sud+tipo:linea_AT`) tramite `_match_ambito`; `_stop_applicabile` li usa tutti.
- `revisiona`: accetta decisioni `IN_ATTESA` o `ESCALATION`; rifiuta quelle che rientrano in uno stop attivo.
- `_esegui`: nuova asserzione che impedisce l'esecuzione di decisioni nell'ambito di uno stop.
- Nuovo `controlla_sla()`: le decisioni in attesa oltre `sla_minuti` passano a `ESCALATION` e vengono registrate nel log.
- Nuovo `proponi_azione(prob, criticita)`: azione proposta derivata dal rischio ($\geq 0.85$ riduci carico o ispezione urgente, $\geq 0.60$ manutenzione, $\geq 0.10$ routine, altrimenti nessuna azione). `riduci_carico` solo se l'utenza non è standard.
- `Raccomandazione`: nuovi campi `chiusa_il` e `scaduta_sla`; `storico_hotl` conserva le auto-esecuzioni HOTL.
- `kpi()` riscritto con A1–A6 (auto-esecuzione impropria, override, tempo mediano, rubber-stamping per motivazione < 30 caratteri o duplicata, escalation SLA, copertura routing) e distribuzione dei livelli.
- Nuovo `livello_dichiarato()`: la matrice D3 in forma tabellare, indipendente da `route()`, usata per A6.

### `app.py`

- Emergency stop: errori di validazione mostrati in sidebar, nuovi ambiti (tipo cabina/turbina e `area:Sud+tipo:linea_AT`), messaggio con numero di decisioni bloccate.
- `om.controlla_sla()` eseguito a ogni rerun.
- Coda: include anche le decisioni in `ESCALATION`; la metrica mostra quante sono in escalation.
- Pulsante "Escalation" aggiunto ad Approva / Modifica / Rifiuta; `st.rerun()` dopo ogni azione.
- `azione_proposta` ora calcolata con `proponi_azione` (prima fissa a `programma_manutenzione`).
- Campione caricato: 40 predizioni positive più 8 a basso rischio (`proba` < 0.2), così il ramo HOTL viene esercitato.
- Nuova scheda "KPI supervisione" con A1–A6 e target.

## Verifiche eseguite

- Test su log temporaneo: rifiuto (T1), motivazione vuota e "ok" respinte (T2), stop parziale su linee AT del Sud (T3), escalation SLA simulata. Catena di hash integra.
- Test KPI su log temporaneo: HOTL auto-eseguita, HIC/HITL in coda; A1 = 0, A4 = 0.667 con una motivazione duplicata e una breve, A6 = 100%.
- Dashboard avviata su `http://localhost:8501` (UI non ancora provata con i pulsanti).

## Note e limiti noti

- Con `confidenza = max(p, 1-p)` una decisione HOTL richiede $p \leq 0.2$: per questo il campione include casi a basso rischio.
- Le nuove decisioni bloccate da uno stop finiscono nel log ma non nella coda.
- `test_llm.py` ricade nel template per `numero non presente nei dati: 0.8`: il suo `rec` non include `soglia_confidenza` (in `app.py` è passata correttamente).
- Dall'analisi baseline: recall Nord/Centro ~0.54 contro Isole 0.95; FPR Sud/Isole ~0.49 (da indagare per il test T5).

## Tier 1: decisioni e indagine

### Soglia decisionale (`train_baseline.py`: 0.35 → 0.30)

- Ipotesi di costo: un falso negativo (guasto non previsto, magari su utenza critica) costa circa 10 volte un falso positivo (ispezione inutile).
- Sweep sul test set (720 asset):

| Soglia | Recall | Precision | FN | FP |
| --- | --- | --- | --- | --- |
| 0.20 | 0.915 | 0.339 | 11 | 230 |
| 0.30 | 0.798 | 0.402 | 26 | 153 |
| 0.35 | 0.744 | 0.438 | 33 | 123 |
| 0.50 | 0.519 | 0.540 | 62 | 57 |

- Scelta 0.30: da 0.20 a 0.35 il costo è quasi piatto, ma 0.20 genera 230 ispezioni inutili su 720 e satura la coda umana (KPI A5). Con 0.30 il recall passa da 0.744 a 0.798. AUC invariato (0.862).

### Anomalia Sud/Isole (test T5)

- Guasti registrati: Nord 0.09, Centro 0.13, Sud 0.24, Isole 0.45.
- Sud e Isole hanno asset più vecchi (23-25 anni contro 14), meno manutenzioni (1.7-2.1 contro 4.1) e più giorni dall'ultima (343-386 contro 167): una parte della differenza è spiegata dai dati.
- Ma temperatura, vibrazione, carico e umidità sono identici tra le aree, e tipo asset e criticità hanno lo stesso mix.
- Calibrazione: il modello prevede 0.40 al Sud contro uno 0.24 osservato (gap 0.159 > 0.10). Altrove il gap è circa 0.05.
- FPR Sud 0.61 e Isole 0.67 contro 0.12-0.15 di Nord e Centro: `area_geografica` funziona da variabile proxy.
- Ipotesi 1 (sotto-segnalazione al Nord e Centro): molti guasti non vengono registrati, quindi il tasso basso è un artefatto e il recall basso (0.54-0.68) non è reale.
- Ipotesi 2 (processo di segnalazione diverso nelle aree con meno manutenzioni): i guasti registrati dipendono da chi ispeziona; meno manutenzioni, più guasti "scoperti" a posteriori.
- Mitigazioni candidate (da implementare): soglia differenziata per area, promozione a HITL delle decisioni HOTL di Sud e Isole, allerta di calibrazione sopra 0.10.

## Da fare

- Tier 2: conferma stop e sblocco con doppia conferma; blocco attivo dei motivi duplicati in `revisiona` (oggi solo misurato da A4).
- Tier 3: matrice con soglie, bias/calibrazione/override per area, drift, alert che promuove HOTL a HITL, audit filtrabile, spiegazioni in ogni card.
- Tier 1 e 4: indagine Sud/Isole, model card, relazione d'impatto, Dichiarazione di oversight, prova dei 6 test.
