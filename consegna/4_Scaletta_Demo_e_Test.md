# Scaletta demo (5-7 minuti) e prove dei test

Prima della demo: `python prova_test_giuria.py` (deve dare 10/10), poi `./run_dashboard.sh` (Windows: `run_dashboard.bat`) dalla cartella del kit. Aprire la dashboard almeno 30 secondi prima: il primo caricamento genera le spiegazioni. Con le dipendenze di `requirements.txt` (D-38) i conteggi citati sotto sono quelli che si vedranno.

## Demo

| Tempo     | Cosa mostrare                                   | Cosa dire                                                                                                                                                              |
| --------- | ----------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 0:00-1:00 | Barra KPI e sidebar                             | Scenario per l'operatore; alto rischio AI Act; soglie 0.30 / 0.20 da costo 10:1; AUC 0.868 del kit, il lavoro è sull'oversight (Tier 1)                                |
| 1:00-1:45 | Card AST-01148 (cabina critica Sud): routing    | Circa 6 su 10, confidenza 0.65; matrice HIC/HITL/HOTL con soglie 0.60 e 0.80; questa è HIC (Tier 2A)                                                                   |
| 1:45-2:30 | Stessa card: spiegazione                        | "In parole semplici", vibrazione 8.7 e 451 giorni, incertezza dichiarata, "e se..." a 3 su 10, 3 casi simili tutti guasti, fonte della spiegazione (Tier 3A, T4)       |
| 2:30-3:15 | Stessa card: rifiuto con "ok", poi motivato     | Quattro azioni; "ok" respinto; rifiuto motivato, nessuna esecuzione, punto unico `_esegui`, SLA 30' (Tier 2B, T1, T2)                                                  |
| 3:15-3:35 | Audit trail su AST-01148                        | Chi, cosa, quando, perché; catena di hash (Tier 3C, T6)                                                                                                                |
| 3:35-4:00 | Stop su `area:Sud+tipo:linea_AT`                | Tre granularità; un click più conferma; 7 decisioni bloccate, banner rosso, sblocco a quattro occhi (Tier 2C, T3)                                                      |
| 4:00-5:30 | Bias & drift, Matrice                           | Sud/Isole 0.24 contro 0.45, due ipotesi, tre mitigazioni; utenze standard Nord/Centro e regola D-43; drift, override per area e per revisore; A6 100% (Tier 1, 3B, T5) |
| 5:30-6:30 | Limiti, documenti, provider e deployer          | Cosa NON abbiamo risolto; model card, relazione, dichiarazione; ruoli AI Act (Tier 4)                                                                                  |

## Risposte pronte ai 6 test

| Test | Dove                              | Risposta                                                                                                                                                                                                                            |
| ---- | --------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| T1   | `oversight_manager.py`, `_esegui` | "Ci sono solo due chiamate a `_esegui`: auto-esecuzione HOTL e revisione approvata o modificata. Una rifiutata non arriva lì, e `_esegui` lo verifica di nuovo"                                                                     |
| T2   | Card, KPI A4                      | Vuota e "ok" respinte; fotocopie respinte anche con maiuscole diverse; A4 misura le brevi                                                                                                                                           |
| T3   | Sidebar                           | Ambito `area:Sud+tipo:linea_AT`, motivazione, ATTIVA STOP, Conferma. Mostrare la sezione "Bloccate" e la voce nel log                                                                                                               |
| T4   | Card                              | Far leggere il riquadro "In parole semplici". Se chiedono di staccare la rete o cambiare chiave: la card resta spiegata e la fonte dice `template(fallback:...)`. Guardrail: numeri inventati, gergo, fattore principale non citato |
| T5   | Bias & drift                      | Anomalia Sud/Isole, ipotesi, tre mitigazioni con numeri prima/dopo (model card); recall con intervallo al 95%, gruppi incrociati e vigilanza su Nord e Centro (D-43..D-45) |
| T6   | Audit trail                       | "Ricostruisci una decisione" in pochi secondi; per la manomissione: `prova_test_giuria.py` mostra che cambiare una motivazione rompe la catena                                                                                      |

## Domande probabili

- **Perché non avete migliorato il modello?** La guida lo sconsiglia; e il problema principale è nelle etichette, non nell'algoritmo.
- **Perché l'LLM?** Solo per i dettagli tecnici, con guardrail e fallback. La parte che deve capire chiunque è a regole fisse.
- **Chi è provider e chi deployer?** Vedi Dichiarazione di oversight, ultima sezione.
