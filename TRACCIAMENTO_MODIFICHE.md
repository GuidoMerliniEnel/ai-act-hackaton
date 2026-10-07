# Tracciamento modifiche · EnerGuard (7 ottobre 2026)

Registro cronologico di ciò che è stato cambiato rispetto allo starter kit, con il motivo.

## Registro delle decisioni (per la presentazione)

Ogni decisione ha un ID citato nel codice come commento `DECISIONE:`. "Origine" indica se la scelta è del gruppo, del kit (default mantenuto e motivato) o tecnica.

### Modello e dati (Tier 1)

| ID   | Decisione                                                           | Razionale                                                                                                                                                    | Origine | Dove                         |
| ---- | ------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------- | ---------------------------- |
| D-01 | Soglia 0.30 per utenze standard (prima 0.35)                        | Un guasto non previsto costa circa 10 volte un'ispezione inutile (ipotesi dichiarata). 0.20 darebbe 230 ispezioni inutili su 720 e saturerebbe la coda umana | Gruppo  | `train_baseline.py` `SOGLIE` |
| D-02 | Soglia 0.20 per utenze alte e critiche                              | L'HIC protegge solo ciò che supera la soglia: un guasto mancato su un ospedale non entra mai in coda. FN su critiche/alte da 3/6 a 1/1                       | Gruppo  | `train_baseline.py` `SOGLIE` |
| D-03 | `area_geografica` fuori dal modello, tenuta per monitoraggio e stop | Fa da proxy del label bias. Senza area AUC 0.868 (da 0.862), gap di recall 0.41 → 0.22                                                                       | Gruppo  | `utils_io.prepara_feature`   |
| D-04 | Ipotesi: sotto-segnalazione dei guasti al Sud                       | Sud e Isole hanno profili quasi identici ma guasti registrati 0.24 contro 0.45; solo il Sud è mal calibrato                                                  | Gruppo  | `TRACCIAMENTO` § Anomalia    |
| D-05 | Nessun aumento di soglia al Sud                                     | I "falsi positivi" del Sud possono essere guasti veri non registrati: alzare la soglia amplificherebbe il bias (recall Sud 0.88 → 0.65)                      | Gruppo  | —                            |
| D-06 | Recall basso di Nord/Centro dichiarato come limite                  | I guasti mancati non hanno segnali dai sensori (vibrazione 2.8 contro 4.6); calibrazione corretta, quindi non è label bias                                   | Gruppo  | Relazione d'impatto          |
| D-07 | Confidenza = $\max(p, 1-p)$                                         | Default del kit, semplice e spiegabile. Limite: con soglia 0.80 il caso HOTL richiede $p \leq 0.20$                                                          | Kit     | `train_baseline.py`          |

### Supervisione umana (Tier 2)

| ID   | Decisione                                                                                                                                                                                | Razionale                                                                                                                                    | Origine       | Dove                           |
| ---- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- | ------------- | ------------------------------ |
| D-08 | Routing: HIC se utenza critica o riduzione carico su utenza alta; HITL se $P \geq 0.60$, confidenza < 0.80, area con allerta o azione non leggera; HOTL solo per routine a basso rischio | Il veto umano assoluto dove l'errore è irreversibile (ospedali); l'AI agisce da sola solo dove l'errore costa poco ed è reversibile (canvas) | Kit + gruppo  | `oversight_manager.route`      |
| D-09 | Azione proposta da regole: ≥ 0.85 riduci carico (solo utenze non standard) o ispezione urgente; ≥ 0.60 manutenzione; ≥ 0.10 routine                                                      | Il kit proponeva sempre "manutenzione": l'azione deve crescere con il rischio                                                                | Tecnica       | `proponi_azione`               |
| D-10 | Un solo punto di esecuzione con controlli                                                                                                                                                | Una decisione rifiutata, in attesa, HIC auto-eseguita o sotto stop non può raggiungere `_esegui` (test T1)                                   | Kit + tecnica | `_esegui`                      |
| D-11 | Motivazione obbligatoria ≥ 15 caratteri; motivazioni fotocopia bloccate; < 30 caratteri misurate                                                                                         | Una motivazione vuota, "ok" o copiata non è un giudizio (test T2, KPI A4)                                                                    | Kit + tecnica | `revisiona`                    |
| D-12 | SLA 30 minuti: oltre, ESCALATION; escalation anche manuale                                                                                                                               | Una decisione non revisionata non viene mai eseguita in silenzio                                                                             | Kit + tecnica | `controlla_sla`                |
| D-13 | Stop a tre granularità più combinazioni (es. linee AT del Sud), anche sulla coda esistente                                                                                               | "Fermare" vale anche per ciò che è già in coda; sotto stop nessuna revisione (test T3)                                                       | Tecnica       | `attiva_stop`, `_match_ambito` |
| D-14 | Attivazione stop: un click più conferma, motivazione obbligatoria                                                                                                                        | Rapido ma non accidentale (test T3)                                                                                                          | Tecnica       | `app.py` sidebar               |
| D-15 | Riattivazione: motivazione, presa visione e secondo operatore diverso                                                                                                                    | Togliere uno stop è più rischioso che metterlo: principio dei quattro occhi (Art. 14(5))                                                     | Tecnica       | `disattiva_stop`               |
| D-16 | Decisioni bloccate restano bloccate dopo lo sblocco; rientrano solo se risottomesse, una volta, rivalutate da zero                                                                       | Evita rumore e derive: nessuna decisione presa prima dell'incidente riparte in automatico                                                    | Gruppo        | `risottometti`                 |
| D-17 | KPI A1–A6 in dashboard; A6 confronta il routing con una copia separata della matrice dichiarata                                                                                          | Un sistema che non misura la propria supervisione non è supervisionabile                                                                     | Tecnica       | `kpi`, `livello_dichiarato`    |
| D-18 | Campione demo: 40 positive più 8 a basso rischio                                                                                                                                         | Senza casi a basso rischio il ramo HOTL non si vedrebbe mai                                                                                  | Tecnica       | `app.py` bootstrap             |

### Monitoraggio e spiegabilità (Tier 3)

| ID   | Decisione                                                                                                                                                            | Razionale                                                                                                                                                                                                                | Origine             | Dove                                      |
| ---- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------- | ----------------------------------------- |
| D-19 | Allerta di calibrazione > 0.10 che promuove a HITL le decisioni HOTL dell'area                                                                                       | Il bias nelle etichette non si corregge nel modello: lo gestisce la supervisione umana. Oggi scatta solo per il Sud (gap 0.177)                                                                                          | Gruppo              | `bias_detector`, `imposta_promozioni`     |
| D-20 | Spiegazioni con LLM Azure, guardrail e fallback al template; limite risposta 2000 token                                                                              | Più leggibili per l'operatore nei dettagli tecnici; con 400 token la risposta era vuota. Accettabile perché l'LLM non decide, i guardrail scartano numeri inventati e la parte per i non esperti è a regole fisse (D-33) | Gruppo (confermata) | `explainer.py`                            |
| D-21 | Soglie "sopra la norma" / "molto sopra" = 75° e 90° percentile della flotta                                                                                          | Con le soglie del kit il 68% degli asset risultava "sopra la norma" per giorni dall'ultima manutenzione: un giudizio che vale per tutti non informa                                                                      | Tecnica             | `explainer.ETICHETTE`                     |
| D-22 | Nella spiegazione prima i fattori che aumentano il rischio                                                                                                           | Il "perché" deve spiegare la raccomandazione: prima il fattore principale poteva ridurre il rischio. Ora 10 card su 10 partono da un fattore di rischio; incoerenze giudizio/direzione 3 su 30                           | Tecnica             | `estrai_fattori`                          |
| D-23 | I tre fattori elencati sotto ogni spiegazione, con la loro direzione                                                                                                 | Anche se l'LLM riassume, l'operatore vede sempre i tre fattori (KPI B1, test T4)                                                                                                                                         | Tecnica             | `app.py` card                             |
| D-24 | Spiegazioni delle card visibili generate in parallelo; log protetto da lock                                                                                          | Primo caricamento da circa 30 s a 5 s. Senza lock, scritture concorrenti romperebbero la catena di hash                                                                                                                  | Tecnica             | `app.py`, `audit_logger.log`              |
| D-25 | Matrice colorata con il livello della matrice dichiarata, soglie tratteggiate e conteggi                                                                             | L'operatore vede a colpo d'occhio dove decide l'AI; il colore viene dalla stessa regola usata dal codice, non da un disegno a parte                                                                                      | Tecnica             | `app.py` scheda Matrice                   |
| D-26 | Drift su 12 "settimane" simulate (blocchi consecutivi del test set): accuracy, recall, confidenza media                                                              | Il dataset non ha date; la guida chiede un drift simulato. Limite dichiarato                                                                                                                                             | Kit + tecnica       | `drift_settimanale`                       |
| D-27 | Allerta drift se l'accuracy resta sotto riferimento − 0.10 per 2 settimane consecutive; se scatta, nessuna auto-esecuzione in nessuna area                           | Una settimana sola è rumore (oscillazione osservata ±0.08); due di fila sono un segnale. Sui dati attuali non scatta                                                                                                     | Tecnica             | `allerta_drift`, bootstrap                |
| D-28 | Allerta override se un'area supera il doppio del tasso medio, con almeno 3 revisioni                                                                                 | Esempio di segnale osservabile dal canvas; il minimo evita allerte su 1-2 casi                                                                                                                                           | Gruppo (canvas)     | `override_per_area`                       |
| D-29 | Audit: ricostruzione di una decisione per asset (chi, cosa, quando, perché, AI approvata o corretta), log filtrabile per asset, attore e periodo, export CSV e JSONL | Test T6 e KPI D3: meno di 60 s, senza aprire il file                                                                                                                                                                     | Tecnica             | `app.py` scheda Audit                     |
| D-30 | Integrità della catena sempre visibile in sidebar                                                                                                                    | La manomissione deve essere evidente in ogni schermata, non solo nella scheda Audit                                                                                                                                      | Tecnica             | `app.py` sidebar                          |
| D-31 | Riquadro "In parole semplici" in cima a ogni card, per un operatore non esperto: semaforo, frase, cosa fare, avvertenze                                              | Il test T4 lo fa un giurato non tecnico; un operatore stanco a fine turno deve capire in pochi secondi. I dettagli tecnici restano sotto                                                                                 | Gruppo              | `explainer.guida_semplice`, `app.py` card |
| D-32 | Probabilità detta come "circa N su 10"; azioni in linguaggio quotidiano ("mandare subito una squadra a controllare")                                                 | Una frequenza si capisce meglio di "P = 0.64"; il nome tecnico dell'azione resta nei dettagli                                                                                                                            | Tecnica             | `guida_semplice`, `AZIONI_SEMPLICI`       |
| D-33 | Riquadro generato da regole fisse, non dall'LLM                                                                                                                      | Istantaneo, ripetibile, nessun numero inventato e nessuna dipendenza dalla rete: la parte che deve capire chiunque non può dipendere da un servizio esterno                                                              | Tecnica             | `guida_semplice`                          |
| D-34 | Scenario "e se...": il modello rifà la previsione con il fattore principale riportato alla mediana della flotta, e dice se l'intervento sarebbe ancora richiesto     | Spiegazione contrastiva, livello 4 della rubrica: mostra che cosa dovrebbe cambiare perché cambi la raccomandazione. È calcolata, non scritta a mano                                                                     | Tecnica             | `explainer.scenario_media`                |
| D-35 | Script `prova_test_giuria.py` che esegue i 6 test della giuria su log temporanei                                                                                     | Prova generale ripetibile prima della demo; non tocca il log reale né `.env`. Oggi 8/8 verifiche superate                                                                                                                | Tecnica             | `prova_test_giuria.py`                    |

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
| `79baf23` | Tier 1: metriche disaggregate e punti di discussione                |
| `7effb0a` | Tier 1: correzione ipotesi e decisioni del gruppo                   |
| `ad8cfd0` | Mitigazione: area fuori dal modello, soglie per criticità           |
| `f580a5e` | Mitigazione: allerta di calibrazione con promozione a HITL          |
| `bbf3264` | Tier 2 chiuso e registro decisioni                                  |
| `2f738b2` | Tier 3: spiegazioni (D-21..D-24)                                    |
| `772495f` | Tier 3: matrice, drift, override per area, audit (D-25..D-30)       |
| `abec779` | Card "In parole semplici" con scenario "e se..." (D-31..D-34)       |
| (questo)  | Tier 4: documenti di consegna e prova dei 6 test (D-35)             |

Backup dello stato precedente al rollback: `%TEMP%\energuard_stato_finale`.

## Setup

- Installate le dipendenze di `requirements.txt` e `pypdf` (usato solo per leggere i PDF della documentazione).
- Eseguito `train_baseline.py`: AUC 0.862 sul kit originale, 0.868 dopo la mitigazione D-03 (area fuori dal modello); generati `modello.joblib` e `predizioni.csv`.
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
- **Prova dal vivo nella dashboard (Tier 2 chiuso)**:
  - T2: rifiuto di AST-00869 con motivazione "ok" respinto con messaggio.
  - T1: rifiuto con motivazione vera; la decisione esce dalla coda (43 → 42), nessuna `[ESECUZIONE]` nel terminale, evento `revisione_RIFIUTATA` nel log con motivazione e operatore.
  - T3: stop su `area:Sud+tipo:linea_AT` con conferma; 8 decisioni bloccate (coda 42 → 34), restano attive la turbina del Sud e la linea AT del Nord; stato "STOP ATTIVI" in sidebar; evento nel log con motivazione e ID bloccati.
  - Sblocco: con lo stesso operatore come conferma respinto; con OP-007 accettato e registrato (`confermato_da`). Le 8 decisioni restano bloccate.
  - Catena di hash integra (415 record).
- **Tier 3**:
  - Spiegazioni sulle 10 card di testa: 10 su 10 dall'LLM, nessun fallback, 4.8 s in parallelo, catena integra.
  - Drift: sui dati reali nessuna allerta (accuracy minima 0.633, soglia 0.617); due settimane simulate sotto soglia la fanno scattare, una sola no.
  - Override: con il Nord al 100% contro una media del 36% scatta l'allerta.
  - Matrice sul test set: 60 HIC, 339 HITL, 321 HOTL.
  - Manomissione (T6): su una copia del log, cambiata la motivazione di un rifiuto alla riga 403; la verifica si ferma a 402 record. Log reale integro (474 record).
  - Dashboard riavviata: tutte le schede caricate senza errori.
- **Card "In parole semplici"**: provata su tre casi (utenza critica, modello incerto, Sud) e poi nel browser su AST-01148 (cabina primaria critica del Sud): semaforo rosso, "circa 6 su 10", motivo principale, cinque passi, avviso sui dati del Sud, scenario "vibrazione nella media → circa 3 su 10, ma servirebbe comunque un controllo". Corretti in prova il genere grammaticale ("Questo linea AT") e lo scenario che diceva "scenderebbe a 2 su 10" partendo da 2 su 10.
- Test automatici su log temporaneo: sblocco senza secondo operatore respinto, risottomissione sotto stop respinta, risottomissione unica (stato `RISOTTOMESSA`), motivazione fotocopia respinta anche con maiuscole e spazi diversi.

## Note e limiti noti

- Con `confidenza = max(p, 1-p)` una decisione HOTL richiede $p \leq 0.2$: per questo il campione include casi a basso rischio.
- Le decisioni bloccate da uno stop restano visibili in coda (sezione "Bloccate") e vanno risottomesse a mano (D-16).
- Nel campione la probabilità massima è 0.79: `riduci_carico` (≥ 0.85) non viene mai proposto, quindi l'HIC scatta solo per utenze critiche.
- La matrice mostra che con confidenza = $\max(p, 1-p)$ i punti stanno su una "V": la confidenza non aggiunge informazione alla probabilità. Un'alternativa (es. accordo tra gli alberi della foresta) sarebbe più informativa (limite di D-07).
- ~~Primo caricamento lento (circa 30 s)~~: risolto con D-24, ora circa 5 s.
- ~~Spiegazioni controintuitive~~: risolto con D-21 e D-22. Restano 3 casi su 30 in cui un valore "nella norma" alza leggermente il rischio: è coerente con il modello, la direzione è mostrata accanto al fattore.
- ~~`test_llm.py` ricade nel template per `numero non presente nei dati: 0.8`~~: risolto, il suo `rec` ora include `soglia_confidenza` e usa `proponi_azione` come `app.py`.
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

| Area   | n   | Guasti reali | Selezione | Recall | FNR   | FPR   | Precision | Gap recall | Gap calibr. | Allerta      |
| ------ | --- | ------------ | --------- | ------ | ----- | ----- | --------- | ---------- | ----------- | ------------ |
| Centro | 189 | 0.127        | 0.201     | 0.542  | 0.458 | 0.152 | 0.342     | 0.411      | 0.052       | recall       |
| Nord   | 300 | 0.093        | 0.170     | 0.679  | 0.321 | 0.118 | 0.373     | 0.274      | 0.056       | recall       |
| Sud    | 143 | 0.238        | 0.671     | 0.882  | 0.118 | 0.606 | 0.312     | 0.071      | 0.159       | calibrazione |
| Isole  | 88  | 0.489        | 0.807     | 0.953  | 0.047 | 0.667 | 0.577     | 0.000      | 0.048       | nessuna      |

| Tipo asset      | n   | Guasti reali | Selezione | Recall | FNR   | FPR   | Precision | Gap recall | Gap calibr. | Allerta |
| --------------- | --- | ------------ | --------- | ------ | ----- | ----- | --------- | ---------- | ----------- | ------- |
| trasformatore   | 271 | 0.159        | 0.362     | 0.744  | 0.256 | 0.289 | 0.327     | 0.127      | 0.094       | nessuna |
| cabina_primaria | 135 | 0.156        | 0.348     | 0.762  | 0.238 | 0.272 | 0.340     | 0.109      | 0.098       | nessuna |
| linea_AT        | 171 | 0.199        | 0.345     | 0.824  | 0.176 | 0.226 | 0.475     | 0.047      | 0.051       | nessuna |
| turbina_eolica  | 143 | 0.217        | 0.364     | 0.871  | 0.129 | 0.223 | 0.519     | 0.000      | 0.041       | nessuna |

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

| Indicatore                   | Prima (area nel modello, soglia unica 0.30) | Dopo          |
| ---------------------------- | ------------------------------------------- | ------------- |
| AUC                          | 0.862                                       | 0.868         |
| Recall globale               | 0.798                                       | 0.837         |
| Guasti mancati (FN)          | 26                                          | 21            |
| FN su utenze critiche / alte | 3 / 6                                       | 1 / 1         |
| Ispezioni inutili (FP)       | 153                                         | 183           |
| Gap di recall tra aree       | 0.411 (Centro)                              | 0.216 (Nord)  |
| Recall Nord / Centro         | 0.679 / 0.542                               | 0.714 / 0.750 |
| FPR Isole                    | 0.667                                       | 0.622         |
| Gap calibrazione Sud         | 0.159                                       | 0.177         |

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

- Tier 2: completato.
- Tier 3: completato.
- Tier 1: completato.
- Tier 4: documenti ufficiali di consegna in `consegna/` (model card, relazione d'impatto, Dichiarazione di oversight, scaletta demo e risposte ai test); `prova_test_giuria.py` 8/8. Versione inglese di supporto in `docs/compliance/` (sito Zensical). Resta: revisione dei documenti da parte del gruppo e prova della demo a voce.

## Allineamento OSPO

- Repository allineato alle linee guida [Enel OSPO](https://github.com/ENEL-GICT-PTG/OSPO): `LICENSE` (Apache-2.0), `NOTICE`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, `.github/CODEOWNERS`, template di issue e PR, header SPDX nei sorgenti.
- Sito di documentazione Zensical in `docs/` (inglese) con tema Enel Design System; workflow `docs.yml` per GitHub Pages.
- Da [reference_architectures](https://github.com/ENEL-GICT-PTG/reference_architectures): istruzioni Copilot OP35/OP36, `AGENTS.md`, agente tech writer, skill `enel-design-system`, `renovate.json5` e gate di sicurezza e licenze in `ci.yml`.
