# Dichiarazione di oversight · EnerGuard

La matrice di routing è implementata in `OversightManager.route()` e, in copia indipendente, in `livello_dichiarato()`: il KPI A6 misura che il codice faccia ciò che questo documento dichiara (oggi 100%).

## Matrice di routing

Le regole si applicano nell'ordine: vale la prima che scatta.

| #   | Condizione                                                     | Livello  | Perché                                                                                                           |
| --- | -------------------------------------------------------------- | -------- | ---------------------------------------------------------------------------------------------------------------- |
| 1   | Utenza **critica** (ospedali, infrastrutture essenziali)       | **HIC**  | Un errore può interrompere la fornitura a un ospedale: effetto irreversibile nell'immediato. Solo l'umano decide |
| 2   | Proposta di **riduzione del carico** su utenza **alta**        | **HIC**  | Ridurre il carico è un'azione con effetto diretto sulle persone servite                                          |
| 3   | Probabilità di guasto **≥ 0.60**                               | **HITL** | Rischio alto: serve un giudizio umano prima di mandare una squadra                                               |
| 4   | Confidenza **< 0.80**                                          | **HITL** | Il modello è incerto: il caso è vicino al "testa o croce"                                                        |
| 5   | Area con **allerta di calibrazione o di drift**                | **HITL** | I dati di quell'area sono sospetti: niente auto-esecuzione finché l'allerta resta attiva (D-19, D-27)            |
| 6   | Area con **allerta di gap di recall** e probabilità **≥ 0.10** | **HITL** | Dove il modello manca più guasti (oggi Nord e Centro) anche l'ispezione di routine passa da un umano (D-43)     |
| 7   | Azione leggera (**nessuna azione** o **ispezione di routine**) | **HOTL** | Errore a costo basso e pienamente reversibile: il sistema agisce, l'umano rivede dopo                            |
| 8   | Tutto il resto                                                 | **HITL** | Default prudente                                                                                                 |

### Perché proprio queste soglie

- **0.60 sul rischio** e **0.80 sulla confidenza**: default del kit, mantenuti. Con la confidenza = $\max(p, 1-p)$ una decisione va in HOTL solo se $p \leq 0.20$: l'AI agisce da sola solo quando è quasi certa che non ci sia un guasto.
- **Soglie di intervento per criticità** (0.20 alte/critiche, 0.30 standard): vedi model card (D-01, D-02).
- Sul test set: 60 HIC, 422 HITL, 238 HOTL. La regola 6 sposta 83 decisioni di Nord e Centro da HOTL a HITL e porta da 6 a 2 i guasti reali che sarebbero stati auto-eseguiti senza revisione (i 2 rimasti sono delle Isole).

## Regole del flusso umano

| Regola                                                            | Valore                                                                         | Perché                                                                        |
| ----------------------------------------------------------------- | ------------------------------------------------------------------------------ | ----------------------------------------------------------------------------- |
| Motivazione per approvare, modificare, rifiutare, fare escalation | ≥ 15 caratteri, non identica a una già usata                                   | Senza motivazione non c'è giudizio né audit (D-11)                            |
| SLA di revisione HITL                                             | 30 minuti, poi ESCALATION                                                      | Una decisione non revisionata non viene mai eseguita in silenzio (D-12)       |
| Esecuzione                                                        | Un solo punto (`_esegui`)                                                      | Una decisione rifiutata, in attesa, HIC o sotto stop non può arrivarci (D-10) |
| Stop                                                              | Globale, per area, per tipo o combinazione; un click più conferma; motivazione | Vale anche per la coda esistente (D-13, D-14)                                 |
| Sblocco                                                           | Motivazione, presa visione, secondo operatore diverso                          | Togliere uno stop è più rischioso che metterlo (D-15)                         |
| Dopo lo sblocco                                                   | Le decisioni bloccate restano bloccate; si risottomettono una per una          | Nessuna decisione presa prima dell'incidente riparte da sola (D-16)           |

## Segnali di allarme monitorati

| Segnale                        | Soglia                                   | Effetto                                    |
| ------------------------------ | ---------------------------------------- | ------------------------------------------ |
| Gap di recall tra aree o tipi  | > 0.15                                   | Allerta in dashboard; nell'area HOTL solo sotto 0.10 di rischio (D-43) |
| Gap di calibrazione di un'area | > 0.10                                   | Allerta e promozione HOTL → HITL nell'area |
| Accuracy settimanale           | < riferimento − 0.10 per 2 settimane     | Allerta e nessuna auto-esecuzione ovunque  |
| Override di un'area            | > doppio della media, almeno 3 revisioni | Allerta: verificare il modello nell'area   |
| Rubber-stamping (A4)           | > 10%                                    | Motivazioni brevi o fotocopia              |
| Integrità del log              | Catena interrotta                        | Allerta in ogni schermata                  |

## Ruoli (domanda finale della guida)

- **Provider**: chi sviluppa il sistema (nel nostro caso il team; nel reale l'unità IT/data o un fornitore). Obblighi: governance e qualità dei dati (Art. 10), documentazione tecnica, accuratezza e robustezza, logging by design (Art. 12), trasparenza verso il deployer (Art. 13, model card), progettazione per la supervisione umana (Art. 14).
- **Deployer**: l'operatore di rete che usa il sistema in control room. Obblighi: assegnare la supervisione a persone competenti e formate (Art. 14, Art. 26), usarlo secondo le istruzioni, monitorarlo, conservare i log, segnalare incidenti e rischi.
