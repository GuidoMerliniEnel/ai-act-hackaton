# Tracciamento modifiche · EnerGuard (7 ottobre 2026)

Registro cronologico di ciò che è stato cambiato rispetto allo starter kit, con il motivo.

## Cronologia git

Il kit è sotto git (`main`). Le modifiche sono state ripristinate allo stato originale e reintrodotte come commit separati; nel codice i TODO risolti sono sostituiti da commenti `DECISIONE:` con il razionale. `.env`, `modello.joblib`, `predizioni.csv` e `audit_trail.jsonl` sono ignorati.

| Commit    | Contenuto                                                           |
| --------- | ------------------------------------------------------------------- |
| `2b69a86` | Baseline: starter kit originale                                     |
| `9315609` | LLM: `max_completion_tokens` 400 → 2000                             |
| `2f0556a` | Tier 2: stop sulla coda esistente, ambiti combinati, escalation SLA |
| `8672ebf` | Tier 2: azione da regole, KPI A1–A6, scheda KPI, campione HOTL      |
| `4687e92` | Tracciamento: cronologia git                                        |
| `5e10d1d` | Tier 1: soglia 0.30 e indagine Sud/Isole                            |

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

| Soglia | Recall | Precision | FN  | FP  |
| ------ | ------ | --------- | --- | --- |
| 0.20   | 0.915  | 0.339     | 11  | 230 |
| 0.30   | 0.798  | 0.402     | 26  | 153 |
| 0.35   | 0.744  | 0.438     | 33  | 123 |
| 0.50   | 0.519  | 0.540     | 62  | 57  |

- Scelta 0.30: da 0.20 a 0.35 il costo è quasi piatto, ma 0.20 genera 230 ispezioni inutili su 720 e satura la coda umana (KPI A5). Con 0.30 il recall passa da 0.744 a 0.798. AUC invariato (0.862).

### Anomalia Sud/Isole (test T5)

- Guasti registrati: Nord 0.09, Centro 0.13, Sud 0.24, Isole 0.45.
- Sud e Isole hanno asset più vecchi (23-25 anni contro 14), meno manutenzioni (1.7-2.1 contro 4.1) e più giorni dall'ultima (343-386 contro 167): una parte della differenza è spiegata dai dati.
- Ma temperatura, vibrazione, carico e umidità sono identici tra le aree, e tipo asset e criticità hanno lo stesso mix.
- Calibrazione: il modello prevede 0.40 al Sud contro uno 0.24 osservato (gap 0.159 > 0.10). Altrove il gap è circa 0.05.
- FPR Sud 0.61 e Isole 0.67 contro 0.12-0.15 di Nord e Centro: `area_geografica` funziona da variabile proxy.
- **Correzione**: il confronto corretto è Sud contro Isole, non contro il Nord. Profili quasi identici (età 23 contro 25 anni, manutenzioni 2.1 contro 1.7, giorni dall'ultima 343 contro 386) ma guasti registrati 0.24 contro 0.45. A parità di rischio (vibrazione ≥ 6 o età ≥ 20): Sud 0.26, Isole 0.49.
- Ipotesi principale: **sotto-segnalazione dei guasti al Sud**. Il modello, guardando i sensori, si aspetta per il Sud un tasso simile alle Isole (0.40) e osserva 0.24; il Sud è l'unica area mal calibrata.
- Ipotesi alternativa: processi di registrazione diversi tra territori (chi ispeziona, quali guasti vengono classificati come tali). I dati non permettono di distinguerle: serve una verifica sul campo.

### Metriche disaggregate (soglia 0.30, test set 720 asset, recall globale 0.798)

Gap di recall = recall massimo del gruppo meno recall del gruppo (allerta sopra 0.15). Gap di calibrazione = probabilità media predetta meno tasso osservato (allerta sopra 0.10).

| Area | n | Guasti reali | Selezione | Recall | FNR | FPR | Precision | Gap recall | Gap calibr. | Allerta |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Centro | 189 | 0.127 | 0.201 | 0.542 | 0.458 | 0.152 | 0.342 | 0.411 | 0.052 | recall |
| Nord | 300 | 0.093 | 0.170 | 0.679 | 0.321 | 0.118 | 0.373 | 0.274 | 0.056 | recall |
| Sud | 143 | 0.238 | 0.671 | 0.882 | 0.118 | 0.606 | 0.312 | 0.071 | 0.159 | calibrazione |
| Isole | 88 | 0.489 | 0.807 | 0.953 | 0.047 | 0.667 | 0.577 | 0.000 | 0.048 | nessuna |

| Tipo asset | n | Guasti reali | Selezione | Recall | FNR | FPR | Precision | Gap recall | Gap calibr. | Allerta |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| trasformatore | 271 | 0.159 | 0.362 | 0.744 | 0.256 | 0.289 | 0.327 | 0.127 | 0.094 | nessuna |
| cabina_primaria | 135 | 0.156 | 0.348 | 0.762 | 0.238 | 0.272 | 0.340 | 0.109 | 0.098 | nessuna |
| linea_AT | 171 | 0.199 | 0.345 | 0.824 | 0.176 | 0.226 | 0.475 | 0.047 | 0.051 | nessuna |
| turbina_eolica | 143 | 0.217 | 0.364 | 0.871 | 0.129 | 0.223 | 0.519 | 0.000 | 0.041 | nessuna |

Cosa dicono i numeri:

- Per area il gap di recall è 0.41 (Centro) e 0.27 (Nord), ben oltre la soglia 0.15: al Nord e al Centro il modello manca un guasto su due o su tre.
- Al Sud e sulle Isole il modello sovra-seleziona (67% e 81% degli asset segnalati) con FPR di 0.61 e 0.67: molte ispezioni inutili. Gap di selezione tra aree: 0.637.
- Per tipo di asset nessun gap supera 0.15, ma trasformatori e cabine primarie si avvicinano (0.13 e 0.11) e sono i più critici per la fornitura.
- La calibrazione è il segnale più netto del label bias: solo il Sud supera 0.10 (0.159).

Da discutere nel gruppo:

1. Il recall basso di Nord e Centro è un difetto del modello o un effetto di guasti non registrati? Cosa cambierebbe nella soglia per area?
2. Per Sud e Isole conviene alzare la soglia (meno falsi positivi) o promuovere a HITL tutte le decisioni (più supervisione, stesso volume)?
3. Il costo 10:1 tra falso negativo e falso positivo regge anche per utenze standard? Per le utenze critiche la decisione è comunque HIC.
4. `area_geografica` va tolta dalle feature del modello, visto che fa da proxy?
5. Quale mitigazione implementiamo e come ne misuriamo l'effetto prima e dopo (serve per il livello 4 della rubrica sulla fairness)?

### Decisioni del gruppo

Evidenze da un esperimento sul test set (modello con e senza area, soglie per area).

1. **Limite del modello, non label bias.** I guasti mancati a Nord e Centro hanno vibrazione media 2.8 contro 4.6 di quelli intercettati: si guastano senza segnali dai sensori. Sono ben calibrati (gap circa 0.05). Lo dichiariamo come limite; abbassare la soglia lo riduce solo al prezzo di molte più ispezioni.
2. **Nessun aumento di soglia al Sud; decisioni del Sud a HITL.** Se i guasti del Sud sono sotto-registrati, molti suoi "falsi positivi" possono essere guasti veri non segnalati. Con soglia 0.40 il recall del Sud scenderebbe da 0.88 a 0.65: il modello amplificherebbe il bias storico. Le Isole sono ben calibrate: FPR alto coerente con un tasso di guasto reale alto, nessuna modifica.
3. **Soglia per criticità.** 10:1 resta l'ipotesi dichiarata per le utenze standard (0.30). Per utenze alte e critiche soglia 0.20: nel test 3 guasti mancati su utenze critiche e 6 su alte, e l'HIC protegge solo ciò che supera la soglia.
4. **`area_geografica` tolta dal modello, tenuta per monitoraggio, stop e fairness.** Senza area: AUC 0.862 → 0.868, gap di recall 0.41 → 0.31, FPR Isole 0.67 → 0.47. Limite dichiarato: il gap di calibrazione del Sud peggiora (0.159 → 0.177), perché il bias sta nelle etichette e il proxy passa da età e manutenzioni.
5. **Pacchetto di mitigazione, misurato prima e dopo**: area fuori dal modello; soglia per criticità; allerta di calibrazione sopra 0.10 che promuove automaticamente a HITL le decisioni HOTL dell'area interessata.

### Mitigazione: prima e dopo (test set 720 asset)

Implementata in `utils_io.prepara_feature` (area esclusa, unico punto usato da training, dashboard e `test_llm.py`) e in `train_baseline.py` (`SOGLIE` per criticità: standard 0.30, alta e critica 0.20).

| Indicatore | Prima (area nel modello, soglia unica 0.30) | Dopo |
| --- | --- | --- |
| AUC | 0.862 | 0.868 |
| Recall globale | 0.798 | 0.837 |
| Guasti mancati (FN) | 26 | 21 |
| FN su utenze critiche / alte | 3 / 6 | 1 / 1 |
| Ispezioni inutili (FP) | 153 | 183 |
| Gap di recall tra aree | 0.411 (Centro) | 0.216 (Nord) |
| Recall Nord / Centro | 0.679 / 0.542 | 0.714 / 0.750 |
| FPR Isole | 0.667 | 0.622 |
| Gap calibrazione Sud | 0.159 | 0.177 |

- Costo della scelta: 30 ispezioni inutili in più per 5 guasti mancati in meno, di cui 7 su utenze critiche e alte. Coerente con il rapporto 10:1.
- Restano due allerte aperte: gap di recall Nord 0.216 (sopra 0.15, limite dichiarato del modello) e calibrazione Sud 0.177, che il modello non può correggere perché il problema è nelle etichette. Per questa serve la terza mitigazione (allerta che promuove a HITL), da implementare.
- Nuova allerta per criticità: le utenze standard hanno recall 0.765 contro 0.971 delle alte (gap 0.206). È voluta: è l'effetto della soglia più bassa sulle utenze più delicate.

### Mitigazione: allerta di calibrazione con promozione automatica a HITL

- `bias_detector.py`: nuovi `calibrazione_per_gruppo`, `gruppi_da_promuovere`, `allerte_calibrazione` (soglia 0.10). I TODO del modulo sono sostituiti dalle decisioni.
- `oversight_manager.py`: `aree_promosse` e `imposta_promozioni` (la modifica viene registrata nel log). In `route()` e nella matrice dichiarata (`livello_dichiarato`) un'area promossa non può andare in HOTL.
- `app.py`: all'avvio la calibrazione per area decide le promozioni; la scheda "Bias & drift" mostra la tabella di calibrazione, l'allerta e le aree promosse.
- Verifica sui dati reali: solo il Sud supera la soglia (0.415 predetto contro 0.238 osservato, gap 0.177) e viene promosso. Stessa decisione a basso rischio: al Nord HOTL auto-eseguita, al Sud HITL in attesa. A1 = 0, A6 = 100%, catena di hash integra.
- È l'alert automatico che modifica il routing richiesto dal Tier 3 (livello 4 della rubrica: il sistema declassa sé stesso).

## Da fare

- Tier 2: conferma stop e sblocco con doppia conferma; blocco attivo dei motivi duplicati in `revisiona` (oggi solo misurato da A4).
- Tier 3: matrice con soglie, drift, override per area, audit filtrabile, spiegazioni in ogni card.
- Tier 1: completato.
- Tier 4: model card, relazione d'impatto, Dichiarazione di oversight, prova dei 6 test.
