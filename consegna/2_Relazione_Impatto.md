# Relazione d'impatto · EnerGuard

## Rischi identificati e mitigazioni implementate

| Rischio | Chi lo subisce | Mitigazione | Come si verifica |
| --- | --- | --- | --- |
| Guasto non previsto su utenza critica (es. ospedale) | Utenze servite, cittadini | Soglia 0.20 per utenze alte/critiche; decisioni su utenze critiche sempre HIC (D-02, D-08) | Guasti mancati su critiche/alte da 3/6 a 1/1 |
| Label bias: guasti del Sud sotto-registrati | Territori del Sud | Area fuori dal modello; nessun aumento di soglia al Sud; allerta di calibrazione che vieta l'auto-esecuzione nell'area (D-03, D-05, D-19) | Gap di calibrazione Sud esposto in dashboard; decisioni HOTL del Sud diventano HITL |
| Automation bias, approvazioni a occhi chiusi | Utenze, squadre | Motivazione obbligatoria, fotocopie bloccate, KPI A3/A4, incertezza sempre visibile (D-11, D-31) | KPI A4 in dashboard; test T2 |
| Azione eseguita nonostante il rifiuto | Utenze, squadre | Un solo punto di esecuzione con controlli (D-10) | Test T1 |
| Impossibilità di fermare una parte del sistema | Tutti | Stop per area, tipo o combinazione, anche sulla coda esistente; sblocco a quattro occhi; decisioni bloccate da risottomettere (D-13..D-16) | Test T3 |
| Coda umana che non regge il carico | Operatori | SLA 30 minuti con escalation; soglia 0.30 invece di 0.20 per non saturare la coda (D-01, D-12) | KPI A5 |
| Spiegazione incomprensibile o inventata | Operatore, giuria | Riquadro semplice a regole fisse; guardrail e fallback per l'LLM (D-20, D-31..D-34) | Test T4 |
| Log manomesso | Auditor | Catena di hash, integrità sempre visibile (D-29, D-30) | Test T6 |

## Cosa NON abbiamo risolto

1. **La sotto-segnalazione al Sud resta un'ipotesi.** I dati non distinguono tra guasti non registrati e processi di registrazione diversi. Serve una verifica sul campo con chi gestisce le segnalazioni nel Sud.
2. **Il modello non vede i guasti senza segnali.** Al Nord e al Centro circa un guasto su quattro arriva senza anomalie nei sensori. Nessuna soglia lo risolve senza moltiplicare le ispezioni.
3. **La correzione del bias è affidata all'umano, non al modello.** Se gli operatori del Sud approvano tutto, la promozione a HITL serve a poco: per questo monitoriamo l'override per area (D-28), ma non abbiamo dati reali per tararlo.
4. **Più ispezioni inutili.** 183 falsi positivi su 720 (30 in più rispetto alla soglia unica): costo operativo accettato, da rivedere con dati di costo reali.
5. **Drift solo simulato** e **SLA non provato sotto carico reale**.
6. **La confidenza scelta è povera**: replica la probabilità. Una misura di accordo tra gli alberi sarebbe più informativa.
7. **Dipendenza da un fornitore LLM esterno** per i dettagli: mitigata dal fallback, ma il testo può variare tra due chiamate.
