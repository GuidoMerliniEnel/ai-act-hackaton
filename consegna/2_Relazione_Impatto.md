# Relazione d'impatto · EnerGuard

| Rischio                                           | Mitigazione                                                                                     | Verifica                        |
| ------------------------------------------------- | ----------------------------------------------------------------------------------------------- | ------------------------------- |
| Guasto non previsto su utenza critica             | Soglia 0.20 per utenze alte/critiche; utenze critiche sempre HIC (D-02, D-08)                   | Guasti mancati 3/6 → 1/1        |
| Label bias: guasti del Sud sotto-registrati       | Area fuori dal modello; soglia del Sud non alzata; Sud sempre in HITL (D-03, D-05, D-19)        | Gap calibrazione Sud in allerta |
| Guasti mancati dove l'AI agisce da sola           | Nord e Centro: niente auto-esecuzione sopra rischio 0.10 (D-43)                                 | Guasti auto-eseguiti 6 → 2      |
| Automation bias e approvazioni "a occhi chiusi"   | Motivazione ≥ 15 caratteri, fotocopie bloccate, statistiche per revisore (D-11, D-40)           | T2, KPI A3/A4                   |
| Azione eseguita nonostante rifiuto o stop         | Un solo punto di esecuzione; stop anche sulla coda esistente, sblocco a quattro occhi (D-10, D-13..D-16) | T1, T3                 |
| Log manomesso                                     | Catena di hash, integrità sempre visibile (D-29, D-30)                                          | T6                              |

**Cosa NON abbiamo risolto**

1. La **sotto-segnalazione al Sud** resta un'ipotesi: serve una verifica sul campo.
2. Al Nord e al Centro circa un guasto su quattro arriva **senza segnali nei sensori**: la supervisione aggiunta (D-43) non aumenta il recall.
3. **Più ispezioni inutili** (183 su 720) e **83 revisioni umane in più**: costi accettati, da tarare con dati reali.
4. Le differenze tra aree poggiano su **24-43 guasti per area**: sono segnali, non prove.
5. **Drift simulato**, costo 10:1 ipotizzato, revisori non differenziati per competenza (D-42).

Elenco completo (14 punti): [allegato](6_Allegato_Versione_Estesa.md).
