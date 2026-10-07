# Model card · EnerGuard

**Scopo.** Stima la probabilità che un asset di rete (trasformatore, linea AT, cabina primaria, turbina eolica) si guasti entro 30 giorni e propone un'azione. **Raccomanda, non decide**: l'operatore approva, corregge, rifiuta o ferma. Nessuna azione su utenze critiche senza decisione umana (D-08).

**Classificazione AI Act: alto rischio**, Allegato III punto 2: componente di sicurezza nella gestione di infrastrutture critiche (fornitura di elettricità).

**Dati.** 2.400 asset sintetici, 10 caratteristiche, target = guasto **registrato** entro 30 giorni (18%). Split 70/30 stratificato, test set di 720 asset. Il target è ciò che è stato registrato, non ciò che è accaduto: Sud e Isole hanno profili quasi identici ma 0.24 contro 0.45 guasti registrati (ipotesi di sotto-segnalazione al Sud, D-04). `area_geografica` è **esclusa dal modello** perché fa da proxy; resta per monitoraggio, stop e fairness (D-03).

**Modello.** Random Forest del kit (300 alberi, pesi bilanciati). Soglia di intervento 0.30 per utenze standard, 0.20 per alte e critiche: un guasto mancato costa circa 10 volte un'ispezione inutile (ipotesi dichiarata, D-01, D-02). **Confidenza = max(p, 1−p)** (D-07).

| Globale | AUC   | Recall | Precision | Guasti mancati | Ispezioni inutili |
| ------- | ----- | ------ | --------- | -------------- | ----------------- |
| Test    | 0.868 | 0.837  | 0.372     | 21             | 183               |

| Area   | Recall [IC 95%]  | FPR   | Gap calibrazione    |
| ------ | ---------------- | ----- | ------------------- |
| Nord   | 0.71 [0.57-0.89] | 0.143 | 0.062               |
| Centro | 0.75 [0.58-0.92] | 0.242 | 0.064               |
| Sud    | 0.88 [0.76-0.97] | 0.688 | **0.178** (allerta) |
| Isole  | 0.93 [0.84-1.00] | 0.622 | −0.033              |

Per tipo di asset recall 0.81-0.90; per criticità standard 0.765, alta 0.971, critica 0.929. Gruppo servito peggio: **utenze standard di Nord e Centro** (recall 0.65-0.68, D-45).

**Spiegazioni.** Riquadro "In parole semplici" a regole fisse con scenario "e se..." e 3 casi simili (D-31..D-34, D-41); dettagli con i 3 fattori SHAP tradotti da un LLM con guardrail e fallback al template, fonte sempre dichiarata (D-20).

**Limiti noti.** Recall più basso a Nord e Centro (guasti senza segnali nei sensori, D-06); sotto-segnalazione al Sud non verificabile dai dati; confidenza che replica la probabilità; drift simulato; costo 10:1 ipotizzato; differenze tra aree su 24-43 guasti per area, quindi segnali e non prove. Elenco completo e analisi del bias: [allegato](6_Allegato_Versione_Estesa.md).
