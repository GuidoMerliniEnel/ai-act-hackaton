# Scaletta demo (5-7 minuti) e prove dei test

Prima della demo: `python prova_test_giuria.py` (deve dare 8/8), poi `./run_dashboard.sh` (Windows: `run_dashboard.bat`) dalla cartella del kit. Aprire la dashboard almeno 30 secondi prima: il primo caricamento genera le spiegazioni. Con le dipendenze di `requirements.txt` (D-38) i conteggi citati sotto sono quelli che si vedranno.

## Demo

| Tempo     | Cosa mostrare                              | Cosa dire                                                                                                                                                                                                                        |
| --------- | ------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 0:00-1:00 | Titolo e coda                              | Il problema: un modello di manutenzione predittiva su asset di rete, alto rischio per l'AI Act. Non abbiamo cercato l'AUC: abbiamo costruito il controllo umano                                                                  |
| 1:00-2:00 | Card HIC (cabina primaria critica del Sud) | Riquadro "In parole semplici": semaforo, "circa 6 su 10", cosa fare, avviso sul Sud, scenario "e se..." (D-31..D-34). Sotto, i dettagli per l'esperto con la fonte                                                               |
| 2:00-3:00 | Rifiuto con "ok", poi con motivazione vera | Il sistema rifiuta "ok"; la decisione esce dalla coda e non viene eseguita; il rifiuto è nel log (T1, T2)                                                                                                                        |
| 3:00-3:45 | Stop su `area:Sud+tipo:linea_AT`           | Un click più conferma; le 7 decisioni sulle linee AT del Sud vengono bloccate, il resto continua. Lo sblocco richiede un secondo operatore (T3, D-13..D-16)                                                                      |
| 3:45-4:15 | Audit trail                                | Ricostruzione della decisione rifiutata: chi, cosa, quando, perché. Catena integra in sidebar (T6)                                                                                                                               |
| 4:15-5:30 | Bias & drift, Matrice                      | Sud e Isole: profili quasi identici, guasti registrati 0.24 contro 0.45. Ipotesi di sotto-segnalazione. Il modello non può correggerlo: abbiamo tolto l'area, non alzato la soglia, e reso il Sud sempre HITL (D-03..D-05, D-19) |
| 5:30-6:30 | Relazione d'impatto                        | Cosa NON abbiamo risolto: ipotesi non verificata, guasti senza segnali, più ispezioni, drift simulato                                                                                                                            |

## Risposte pronte ai 6 test

| Test | Dove                              | Risposta                                                                                                                                                                                                                            |
| ---- | --------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| T1   | `oversight_manager.py`, `_esegui` | "Ci sono solo due chiamate a `_esegui`: auto-esecuzione HOTL e revisione approvata o modificata. Una rifiutata non arriva lì, e `_esegui` lo verifica di nuovo"                                                                     |
| T2   | Card, KPI A4                      | Vuota e "ok" respinte; fotocopie respinte anche con maiuscole diverse; A4 misura le brevi                                                                                                                                           |
| T3   | Sidebar                           | Ambito `area:Sud+tipo:linea_AT`, motivazione, ATTIVA STOP, Conferma. Mostrare la sezione "Bloccate" e la voce nel log                                                                                                               |
| T4   | Card                              | Far leggere il riquadro "In parole semplici". Se chiedono di staccare la rete o cambiare chiave: la card resta spiegata e la fonte dice `template(fallback:...)`. Guardrail: numeri inventati, gergo, fattore principale non citato |
| T5   | Bias & drift                      | Anomalia Sud/Isole, ipotesi, tre mitigazioni con numeri prima/dopo (model card)                                                                                                                                                     |
| T6   | Audit trail                       | "Ricostruisci una decisione" in pochi secondi; per la manomissione: `prova_test_giuria.py` mostra che cambiare una motivazione rompe la catena                                                                                      |

## Domande probabili

- **Perché non avete migliorato il modello?** La guida lo sconsiglia; e il problema principale è nelle etichette, non nell'algoritmo.
- **Perché l'LLM?** Solo per i dettagli tecnici, con guardrail e fallback. La parte che deve capire chiunque è a regole fisse.
- **Chi è provider e chi deployer?** Vedi Dichiarazione di oversight, ultima sezione.
