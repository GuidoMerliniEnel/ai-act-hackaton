# Allegato · versione estesa dei documenti di consegna

Dettagli spostati dai tre documenti sintetici (limiti di pagina della giuria): analisi approfondita del bias, elenco completo dei limiti, regole del flusso umano e segnali di allarme. Versione inglese nel sito `docs/compliance/`.

## Model card · EnerGuard

Sistema di manutenzione predittiva con supervisione umana per asset critici della rete elettrica. Gli ID tra parentesi (D-xx) rimandano al registro decisioni in `TRACCIAMENTO_MODIFICHE.md`.

### Scopo e uso previsto

- **Cosa fa**: stima la probabilità che un asset (trasformatore, linea AT, cabina primaria, turbina eolica) si guasti entro 30 giorni e propone un'azione (nessuna, ispezione di routine, manutenzione, riduzione del carico, ispezione urgente).
- **Chi lo usa**: l'operatore della control room, che approva, corregge, rifiuta o ferma le raccomandazioni.
- **Cosa non fa**: non decide da solo nulla che tocchi utenze critiche, né azioni ad alto rischio o con modello incerto (D-08). Non sostituisce il giudizio di chi conosce l'impianto.
- **Classificazione AI Act**: alto rischio, Annex III punto 2 (componente di sicurezza nella gestione di infrastrutture critiche, fornitura di elettricità). Requisiti pieni dal 2 agosto 2026.

### Dati

- 2.400 asset, 10 caratteristiche (età, temperatura, vibrazione, carico, umidità, manutenzioni, giorni dall'ultima manutenzione, tipo, area, criticità dell'utenza). Target: guasto registrato entro 30 giorni (18% dei casi).
- Split 70/30 stratificato, test set di 720 asset.
- **Il target è ciò che è stato registrato, non necessariamente ciò che è accaduto.** Sud e Isole hanno profili quasi identici ma guasti registrati 0.24 contro 0.45: ipotesi di sotto-segnalazione al Sud (D-04).
- `area_geografica` è esclusa dal modello perché fa da proxy del bias; resta nei dati per monitoraggio, stop e fairness (D-03).

### Modello

- Random Forest (300 alberi, pesi bilanciati), baseline del kit senza ottimizzazioni: il punteggio si gioca sull'oversight, non sull'AUC.
- **Soglie decisionali per criticità**: 0.30 per utenze standard, 0.20 per utenze alte e critiche (D-01, D-02). Ipotesi dichiarata: un guasto non previsto costa circa 10 volte un'ispezione inutile.
- **Confidenza** = $\max(p, 1-p)$, default del kit (D-07). Limite: non aggiunge informazione rispetto alla probabilità (nella matrice i punti formano una "V").

### Prestazioni (test set, 720 asset)

| Globale | AUC   | Recall | Precision | Accuracy | Guasti mancati | Ispezioni inutili |
| ------- | ----- | ------ | --------- | -------- | -------------- | ----------------- |
| Valore  | 0.868 | 0.837  | 0.371     | 0.717    | 21             | 183               |

| Area   | Recall | FPR   | Gap calibrazione    |
| ------ | ------ | ----- | ------------------- |
| Nord   | 0.714  | 0.147 | 0.062               |
| Centro | 0.750  | 0.242 | 0.064               |
| Sud    | 0.882  | 0.688 | **0.177** (allerta) |
| Isole  | 0.930  | 0.622 | −0.033              |

| Tipo asset      | Recall | Criticità utenza | Recall |
| --------------- | ------ | ---------------- | ------ |
| cabina primaria | 0.810  | standard         | 0.765  |
| trasformatore   | 0.814  | alta             | 0.971  |
| linea AT        | 0.824  | critica          | 0.929  |
| turbina eolica  | 0.903  |                  |        |

Prima della mitigazione (area nel modello, soglia unica 0.30): recall 0.798, gap di recall tra aree 0.411, guasti mancati su utenze critiche/alte 3/6, ora 1/1.

### Analisi approfondita del bias

- **Incertezza delle stime** (D-44): ogni area ha solo 24-43 guasti reali nel test set. Recall con intervallo bootstrap al 95%: Nord 0.71 [0.57-0.89], Centro 0.75 [0.58-0.92], Sud 0.88 [0.76-0.97], Isole 0.93 [0.84-1.00]. Gli intervalli si sovrappongono: il gap di recall è un segnale da monitorare, non una differenza dimostrata.
- **Gruppi incrociati** (D-45, almeno 15 asset): il gruppo servito peggio sono le **utenze standard di Centro e Nord** (recall 0.65 e 0.68), invisibile guardando area e criticità separatamente. Il label bias del Sud è concentrato su **trasformatori** (gap di calibrazione +0.25) e **utenze standard** (+0.21); sulle utenze critiche del Sud è quasi assente (+0.03).
- **Proxy residuo**: tolta l'area, le altre caratteristiche la indovinano nel 58% dei casi (contro il 38% del caso), soprattutto tramite giorni dall'ultima manutenzione ed età. Distinguono però a fatica Sud e Isole (67% contro 65%).
- **Profilo a parità di età**: tra 15 e 25 anni il Sud registra 0.24 guasti contro 0.39 delle Isole, oltre 25 anni 0.28 contro 0.54. I sensori sono uguali: conferma l'ipotesi di sotto-segnalazione (D-04).
- **Esposizione all'automazione**: prima di D-43 Nord e Centro avevano la quota più alta di auto-esecuzione (70% e 53%) e la recall più bassa; sul test set 6 guasti reali sarebbero stati auto-eseguiti senza revisione. Con D-43 restano 2 (Isole).

### Spiegazioni

- **Riquadro "In parole semplici"** a regole fisse (D-31..D-34): semaforo, "circa N su 10", cosa fare, avvertenze e scenario "e se..." calcolato rifacendo la previsione con il fattore principale nella media.
- **Dettagli per l'esperto**: fattori SHAP tradotti da un LLM Azure (`gpt-5.6-luna`) con guardrail e fallback automatico al template (D-20, confermata dal gruppo).
- **Casi simili** (D-41): nella card, 3 asset storici dello stesso tipo con sensori simili e il loro esito registrato; avviso che lo storico del Sud può sottostimare i guasti.
- **Perché l'LLM**: testo più naturale nei dettagli. **Perché è accettabile**: l'LLM non decide e non calcola; i guardrail scartano numeri inventati, gergo tecnico e risposte che non citano il fattore principale; ogni spiegazione dichiara la fonte; con rete assente o chiave errata la card resta spiegata. La parte che deve capire chiunque non usa l'LLM.

### Limiti noti

- Il recall di Nord e Centro (0.71-0.75) resta sotto le altre aree: i guasti mancati non mostrano segnali nei sensori (D-06). La supervisione compensa in parte: in quelle aree l'ispezione di routine non è più auto-eseguita (D-43).
- Le utenze standard di Nord e Centro hanno il recall più basso (0.65-0.68): effetto combinato della soglia 0.30 e del limite del modello.
- La sotto-segnalazione al Sud è un'ipotesi; il modello non la può correggere (il problema è nelle etichette). È gestita dalla supervisione: le decisioni del Sud non vengono mai auto-eseguite (D-19).
- Il drift è simulato: il dataset non ha date (D-26).
- Il rapporto di costo 10:1 è un'ipotesi del gruppo, non un dato aziendale.
- 183 ispezioni inutili su 720: è il prezzo di un recall più alto.
- Dipendenze fissate a versioni esatte (D-38): `train_baseline.py` produce gli stessi numeri su ogni macchina con Python da 3.11 (ambiente del kit) a 3.14 (D-46).

## Relazione d'impatto · EnerGuard

### Rischi identificati e mitigazioni implementate

| Rischio                                              | Chi lo subisce            | Mitigazione                                                                                                                                           | Come si verifica                                                                    |
| ---------------------------------------------------- | ------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| Guasto non previsto su utenza critica (es. ospedale) | Utenze servite, cittadini | Soglia 0.20 per utenze alte/critiche; decisioni su utenze critiche sempre HIC (D-02, D-08)                                                            | Guasti mancati su critiche/alte da 3/6 a 1/1                                        |
| Label bias: guasti del Sud sotto-registrati          | Territori del Sud         | Area fuori dal modello; nessun aumento di soglia al Sud; allerta di calibrazione che vieta l'auto-esecuzione nell'area (D-03, D-05, D-19)             | Gap di calibrazione Sud esposto in dashboard; decisioni HOTL del Sud diventano HITL |
| Automation bias, approvazioni a occhi chiusi         | Utenze, squadre           | Motivazione obbligatoria, fotocopie bloccate, KPI A3/A4, incertezza sempre visibile (D-11, D-31)                                                      | KPI A4 in dashboard; test T2                                                        |
| Azione eseguita nonostante il rifiuto                | Utenze, squadre           | Un solo punto di esecuzione con controlli (D-10)                                                                                                      | Test T1                                                                             |
| Impossibilità di fermare una parte del sistema       | Tutti                     | Stop per area, tipo o combinazione, anche sulla coda esistente; sblocco a quattro occhi; decisioni bloccate da risottomettere (D-13..D-16)            | Test T3                                                                             |
| Coda umana che non regge il carico                   | Operatori                 | SLA 30 minuti con escalation; soglia 0.30 invece di 0.20 per non saturare la coda (D-01, D-12)                                                        | KPI A5                                                                              |
| Spiegazione incomprensibile o inventata              | Operatore, giuria         | Riquadro semplice a regole fisse; guardrail e fallback per l'LLM (D-20, D-31..D-34)                                                                   | Test T4                                                                             |
| Log manomesso                                        | Auditor                   | Catena di hash, integrità sempre visibile (D-29, D-30)                                                                                                | Test T6                                                                             |
| Guasti mancati concentrati dove l'AI agisce da sola  | Utenze di Nord e Centro   | Nelle aree con allerta di recall l'ispezione di routine passa da un umano (D-43); recall con intervallo e gruppi incrociati in dashboard (D-44, D-45) | Guasti reali auto-eseguiti sul test set da 6 a 2; tabelle nella scheda Bias & drift |

### Cosa NON abbiamo risolto

1. **La sotto-segnalazione al Sud resta un'ipotesi.** I dati non distinguono tra guasti non registrati e processi di registrazione diversi. Serve una verifica sul campo con chi gestisce le segnalazioni nel Sud.
2. **Il modello non vede i guasti senza segnali.** Al Nord e al Centro circa un guasto su quattro arriva senza anomalie nei sensori. Nessuna soglia lo risolve senza moltiplicare le ispezioni.
3. **La correzione del bias è affidata all'umano, non al modello.** Se gli operatori del Sud approvano tutto, la promozione a HITL serve a poco: per questo monitoriamo l'override per area (D-28), ma non abbiamo dati reali per tararlo.
4. **Più ispezioni inutili.** 183 falsi positivi su 720 (30 in più rispetto alla soglia unica): costo operativo accettato, da rivedere con dati di costo reali.
5. **Drift solo simulato** e **SLA non provato sotto carico reale**.
6. **La confidenza scelta è povera**: replica la probabilità. Una misura di accordo tra gli alberi sarebbe più informativa.
7. **Dipendenza da un fornitore LLM esterno** per i dettagli: mitigata dal fallback, ma il testo può variare tra due chiamate.
8. **Modello non versionato.** Le dipendenze sono fissate a versioni esatte (D-38) e il risultato è riproducibile, ma `modello.joblib` viene riaddestrato a ogni installazione: in produzione servirebbe un registro dei modelli con versione e firma.
9. **Revisori non differenziati per competenza** (D-42): chiunque abbia accesso può decidere anche sulle utenze critiche. Serve definire ruoli e autorizzazioni con l'organizzazione.
10. **Il tempo di lettura per revisore è approssimato** (D-40): misuriamo l'intervallo tra due decisioni, non il tempo effettivo passato sulla card.
11. **Le utenze standard di Nord e Centro sono servite peggio** (recall 0.65-0.68): somma della soglia più alta per le utenze standard e dei guasti senza segnali. D-43 aggiunge supervisione, non recall.
12. **L'area entra ancora nel modello per via indiretta**: età e giorni dall'ultima manutenzione la indovinano nel 58% dei casi. Non la togliamo: sono anche fattori di rischio reali.
13. **Le differenze tra aree non sono statisticamente solide**: 24-43 guasti per area, intervalli di confidenza sovrapposti. Le allerte vanno lette come segnali.
14. **Restano 2 guasti reali auto-eseguiti nelle Isole** (rischio 0.14-0.17), area senza allerta. Più carico umano: D-43 aggiunge 83 decisioni HITL su 720 (KPI A5 da sorvegliare).
15. **L'allerta di calibrazione guarda i punti, non le proporzioni.** Il modello prevede più guasti di quelli registrati quasi ovunque (25 contro 18 ogni 100, effetto dei pesi bilanciati). Ogni 100 guasti attesi ne risultano: Nord 60, Centro 67, Sud 57, Isole 107. Lo scarto supera 0.10 solo al Sud (0.177), ma in proporzione il Nord è vicino: anche lì potrebbe esserci sotto-registrazione, mascherata dal tasso basso. La prova più solida del bias al Sud resta il confronto diretto con le Isole sui dati.

## Dichiarazione di oversight · EnerGuard

La matrice di routing è implementata in `OversightManager.route()` e, in copia indipendente, in `livello_dichiarato()`: il KPI A6 misura che il codice faccia ciò che questo documento dichiara (oggi 100%).

### Matrice di routing

Le regole si applicano nell'ordine: vale la prima che scatta.

| #   | Condizione                                                     | Livello  | Perché                                                                                                           |
| --- | -------------------------------------------------------------- | -------- | ---------------------------------------------------------------------------------------------------------------- |
| 1   | Utenza **critica** (ospedali, infrastrutture essenziali)       | **HIC**  | Un errore può interrompere la fornitura a un ospedale: effetto irreversibile nell'immediato. Solo l'umano decide |
| 2   | Proposta di **riduzione del carico** su utenza **alta**        | **HIC**  | Ridurre il carico è un'azione con effetto diretto sulle persone servite                                          |
| 3   | Probabilità di guasto **≥ 0.60**                               | **HITL** | Rischio alto: serve un giudizio umano prima di mandare una squadra                                               |
| 4   | Confidenza **< 0.80**                                          | **HITL** | Il modello è incerto: il caso è vicino al "testa o croce"                                                        |
| 5   | Area con **allerta di calibrazione o di drift**                | **HITL** | I dati di quell'area sono sospetti: niente auto-esecuzione finché l'allerta resta attiva (D-19, D-27)            |
| 6   | Area con **allerta di gap di recall** e probabilità **≥ 0.10** | **HITL** | Dove il modello manca più guasti (oggi Nord e Centro) anche l'ispezione di routine passa da un umano (D-43)      |
| 7   | Azione leggera (**nessuna azione** o **ispezione di routine**) | **HOTL** | Errore a costo basso e pienamente reversibile: il sistema agisce, l'umano rivede dopo                            |
| 8   | Tutto il resto                                                 | **HITL** | Default prudente                                                                                                 |

### Perché proprio queste soglie

- **0.60 sul rischio** e **0.80 sulla confidenza**: default del kit, mantenuti. Con la confidenza = $\max(p, 1-p)$ una decisione va in HOTL solo se $p \leq 0.20$: l'AI agisce da sola solo quando è quasi certa che non ci sia un guasto.
- **Soglie di intervento per criticità** (0.20 alte/critiche, 0.30 standard): vedi model card (D-01, D-02).
- Sul test set: 60 HIC, 422 HITL, 238 HOTL. La regola 6 sposta 83 decisioni di Nord e Centro da HOTL a HITL e porta da 6 a 2 i guasti reali che sarebbero stati auto-eseguiti senza revisione (i 2 rimasti sono delle Isole).

### Regole del flusso umano

| Regola                                                            | Valore                                                                         | Perché                                                                        |
| ----------------------------------------------------------------- | ------------------------------------------------------------------------------ | ----------------------------------------------------------------------------- |
| Motivazione per approvare, modificare, rifiutare, fare escalation | ≥ 15 caratteri, non identica a una già usata                                   | Senza motivazione non c'è giudizio né audit (D-11)                            |
| SLA di revisione HITL                                             | 30 minuti, poi ESCALATION                                                      | Una decisione non revisionata non viene mai eseguita in silenzio (D-12)       |
| Esecuzione                                                        | Un solo punto (`_esegui`)                                                      | Una decisione rifiutata, in attesa, HIC o sotto stop non può arrivarci (D-10) |
| Stop                                                              | Globale, per area, per tipo o combinazione; un click più conferma; motivazione | Vale anche per la coda esistente (D-13, D-14)                                 |
| Sblocco                                                           | Motivazione, presa visione, secondo operatore diverso                          | Togliere uno stop è più rischioso che metterlo (D-15)                         |
| Dopo lo sblocco                                                   | Le decisioni bloccate restano bloccate; si risottomettono una per una          | Nessuna decisione presa prima dell'incidente riparte da sola (D-16)           |

### Segnali di allarme monitorati

| Segnale                        | Soglia                                   | Effetto                                                                |
| ------------------------------ | ---------------------------------------- | ---------------------------------------------------------------------- |
| Gap di recall tra aree o tipi  | > 0.15                                   | Allerta in dashboard; nell'area HOTL solo sotto 0.10 di rischio (D-43) |
| Gap di calibrazione di un'area | > 0.10                                   | Allerta e promozione HOTL → HITL nell'area                             |
| Accuracy settimanale           | < riferimento − 0.10 per 2 settimane     | Allerta e nessuna auto-esecuzione ovunque                              |
| Override di un'area            | > doppio della media, almeno 3 revisioni | Allerta: verificare il modello nell'area                               |
| Rubber-stamping (A4)           | > 10%                                    | Motivazioni brevi o fotocopia                                          |
| Integrità del log              | Catena interrotta                        | Allerta in ogni schermata                                              |

### Ruoli (domanda finale della guida)

- **Provider**: chi sviluppa il sistema (nel nostro caso il team; nel reale l'unità IT/data o un fornitore). Obblighi: governance e qualità dei dati (Art. 10), documentazione tecnica, accuratezza e robustezza, logging by design (Art. 12), trasparenza verso il deployer (Art. 13, model card), progettazione per la supervisione umana (Art. 14).
- **Deployer**: l'operatore di rete che usa il sistema in control room. Obblighi: assegnare la supervisione a persone competenti e formate (Art. 14, Art. 26), usarlo secondo le istruzioni, monitorarlo, conservare i log, segnalare incidenti e rischi.
