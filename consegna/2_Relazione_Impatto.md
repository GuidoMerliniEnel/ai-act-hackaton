# Relazione d'impatto · EnerGuard

## Rischi identificati e mitigazioni implementate

| Rischio                                              | Chi lo subisce            | Mitigazione                                                                                                                                | Come si verifica                                                                    |
| ---------------------------------------------------- | ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------- |
| Guasto non previsto su utenza critica (es. ospedale) | Utenze servite, cittadini | Soglia 0.20 per utenze alte/critiche; decisioni su utenze critiche sempre HIC (D-02, D-08)                                                 | Guasti mancati su critiche/alte da 3/6 a 1/1                                        |
| Label bias: guasti del Sud sotto-registrati          | Territori del Sud         | Area fuori dal modello; nessun aumento di soglia al Sud; allerta di calibrazione che vieta l'auto-esecuzione nell'area (D-03, D-05, D-19)  | Gap di calibrazione Sud esposto in dashboard; decisioni HOTL del Sud diventano HITL |
| Automation bias, approvazioni a occhi chiusi         | Utenze, squadre           | Motivazione obbligatoria, fotocopie bloccate, KPI A3/A4, incertezza sempre visibile (D-11, D-31)                                           | KPI A4 in dashboard; test T2                                                        |
| Azione eseguita nonostante il rifiuto                | Utenze, squadre           | Un solo punto di esecuzione con controlli (D-10)                                                                                           | Test T1                                                                             |
| Impossibilità di fermare una parte del sistema       | Tutti                     | Stop per area, tipo o combinazione, anche sulla coda esistente; sblocco a quattro occhi; decisioni bloccate da risottomettere (D-13..D-16) | Test T3                                                                             |
| Coda umana che non regge il carico                   | Operatori                 | SLA 30 minuti con escalation; soglia 0.30 invece di 0.20 per non saturare la coda (D-01, D-12)                                             | KPI A5                                                                              |
| Spiegazione incomprensibile o inventata              | Operatore, giuria         | Riquadro semplice a regole fisse; guardrail e fallback per l'LLM (D-20, D-31..D-34)                                                        | Test T4                                                                             |
| Log manomesso                                        | Auditor                   | Catena di hash, integrità sempre visibile (D-29, D-30)                                                                                     | Test T6                                                                             |
| Guasti mancati concentrati dove l'AI agisce da sola  | Utenze di Nord e Centro   | Nelle aree con allerta di recall l'ispezione di routine passa da un umano (D-39); recall con intervallo e gruppi incrociati in dashboard (D-40, D-41) | Guasti reali auto-eseguiti sul test set da 6 a 2; tabelle nella scheda Bias & drift |

## Cosa NON abbiamo risolto

1. **La sotto-segnalazione al Sud resta un'ipotesi.** I dati non distinguono tra guasti non registrati e processi di registrazione diversi. Serve una verifica sul campo con chi gestisce le segnalazioni nel Sud.
2. **Il modello non vede i guasti senza segnali.** Al Nord e al Centro circa un guasto su quattro arriva senza anomalie nei sensori. Nessuna soglia lo risolve senza moltiplicare le ispezioni.
3. **La correzione del bias è affidata all'umano, non al modello.** Se gli operatori del Sud approvano tutto, la promozione a HITL serve a poco: per questo monitoriamo l'override per area (D-28), ma non abbiamo dati reali per tararlo.
4. **Più ispezioni inutili.** 182 falsi positivi su 720 (30 in più rispetto alla soglia unica): costo operativo accettato, da rivedere con dati di costo reali.
5. **Drift solo simulato** e **SLA non provato sotto carico reale**.
6. **La confidenza scelta è povera**: replica la probabilità. Una misura di accordo tra gli alberi sarebbe più informativa.
7. **Dipendenza da un fornitore LLM esterno** per i dettagli: mitigata dal fallback, ma il testo può variare tra due chiamate.
8. **Modello non versionato.** Le dipendenze sono fissate a versioni esatte (D-38) e il risultato è riproducibile, ma `modello.joblib` viene riaddestrato a ogni installazione: in produzione servirebbe un registro dei modelli con versione e firma.
9. **Le utenze standard di Nord e Centro sono servite peggio** (recall 0.65-0.68): somma della soglia più alta per le utenze standard e dei guasti senza segnali. D-39 aggiunge supervisione, non recall.
10. **L'area entra ancora nel modello per via indiretta**: età e giorni dall'ultima manutenzione la indovinano nel 58% dei casi. Non la togliamo: sono anche fattori di rischio reali.
11. **Le differenze tra aree non sono statisticamente solide**: 24-43 guasti per area, intervalli di confidenza sovrapposti. Le allerte vanno lette come segnali.
12. **Restano 2 guasti reali auto-eseguiti nelle Isole** (rischio 0.14-0.17), area senza allerta. Più carico umano: D-39 aggiunge 83 decisioni HITL su 720 (KPI A5 da sorvegliare).
