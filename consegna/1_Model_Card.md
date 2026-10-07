# Model card · EnerGuard

Sistema di manutenzione predittiva con supervisione umana per asset critici della rete elettrica. Gli ID tra parentesi (D-xx) rimandano al registro decisioni in `TRACCIAMENTO_MODIFICHE.md`.

## Scopo e uso previsto

- **Cosa fa**: stima la probabilità che un asset (trasformatore, linea AT, cabina primaria, turbina eolica) si guasti entro 30 giorni e propone un'azione (nessuna, ispezione di routine, manutenzione, riduzione del carico, ispezione urgente).
- **Chi lo usa**: l'operatore della control room, che approva, corregge, rifiuta o ferma le raccomandazioni.
- **Cosa non fa**: non decide da solo nulla che tocchi utenze critiche, né azioni ad alto rischio o con modello incerto (D-08). Non sostituisce il giudizio di chi conosce l'impianto.
- **Classificazione AI Act**: alto rischio, Annex III punto 2 (componente di sicurezza nella gestione di infrastrutture critiche, fornitura di elettricità). Requisiti pieni dal 2 agosto 2026.

## Dati

- 2.400 asset, 10 caratteristiche (età, temperatura, vibrazione, carico, umidità, manutenzioni, giorni dall'ultima manutenzione, tipo, area, criticità dell'utenza). Target: guasto registrato entro 30 giorni (18% dei casi).
- Split 70/30 stratificato, test set di 720 asset.
- **Il target è ciò che è stato registrato, non necessariamente ciò che è accaduto.** Sud e Isole hanno profili quasi identici ma guasti registrati 0.24 contro 0.45: ipotesi di sotto-segnalazione al Sud (D-04).
- `area_geografica` è esclusa dal modello perché fa da proxy del bias; resta nei dati per monitoraggio, stop e fairness (D-03).

## Modello

- Random Forest (300 alberi, pesi bilanciati), baseline del kit senza ottimizzazioni: il punteggio si gioca sull'oversight, non sull'AUC.
- **Soglie decisionali per criticità**: 0.30 per utenze standard, 0.20 per utenze alte e critiche (D-01, D-02). Ipotesi dichiarata: un guasto non previsto costa circa 10 volte un'ispezione inutile.
- **Confidenza** = $\max(p, 1-p)$, default del kit (D-07). Limite: non aggiunge informazione rispetto alla probabilità (nella matrice i punti formano una "V").

## Prestazioni (test set, 720 asset)

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
- **Gruppi incrociati** (D-45, almeno 15 asset): il gruppo servito peggio sono le **utenze standard di Centro e Nord** (recall 0.65 e 0.68), invisibile guardando area e criticità separatamente. Il label bias del Sud è concentrato su **trasformatori** (gap di calibrazione +0.25) e **utenze standard** (+0.21); sulle utenze critiche del Sud è quasi assente (+0.02).
- **Proxy residuo**: tolta l'area, le altre caratteristiche la indovinano nel 57% dei casi (contro il 38% del caso), soprattutto tramite giorni dall'ultima manutenzione ed età. Distinguono però a fatica Sud e Isole (67% contro 65%).
- **Profilo a parità di età**: tra 15 e 25 anni il Sud registra 0.24 guasti contro 0.39 delle Isole, oltre 25 anni 0.28 contro 0.54. I sensori sono uguali: conferma l'ipotesi di sotto-segnalazione (D-04).
- **Esposizione all'automazione**: prima di D-43 Nord e Centro avevano la quota più alta di auto-esecuzione (70% e 53%) e la recall più bassa; sul test set 6 guasti reali sarebbero stati auto-eseguiti senza revisione. Con D-43 restano 2 (Isole).

## Spiegazioni

- **Riquadro "In parole semplici"** a regole fisse (D-31..D-34): semaforo, "circa N su 10", cosa fare, avvertenze e scenario "e se..." calcolato rifacendo la previsione con il fattore principale nella media.
- **Dettagli per l'esperto**: fattori SHAP tradotti da un LLM Azure (`gpt-5.6-luna`) con guardrail e fallback automatico al template (D-20, confermata dal gruppo).
- **Casi simili** (D-41): nella card, 3 asset storici dello stesso tipo con sensori simili e il loro esito registrato; avviso che lo storico del Sud può sottostimare i guasti.
- **Perché l'LLM**: testo più naturale nei dettagli. **Perché è accettabile**: l'LLM non decide e non calcola; i guardrail scartano numeri inventati, gergo tecnico e risposte che non citano il fattore principale; ogni spiegazione dichiara la fonte; con rete assente o chiave errata la card resta spiegata. La parte che deve capire chiunque non usa l'LLM.

## Limiti noti

- Il recall di Nord e Centro (0.71-0.75) resta sotto le altre aree: i guasti mancati non mostrano segnali nei sensori (D-06). La supervisione compensa in parte: in quelle aree l'ispezione di routine non è più auto-eseguita (D-43).
- Le utenze standard di Nord e Centro hanno il recall più basso (0.65-0.68): effetto combinato della soglia 0.30 e del limite del modello.
- La sotto-segnalazione al Sud è un'ipotesi; il modello non la può correggere (il problema è nelle etichette). È gestita dalla supervisione: le decisioni del Sud non vengono mai auto-eseguite (D-19).
- Il drift è simulato: il dataset non ha date (D-26).
- Il rapporto di costo 10:1 è un'ipotesi del gruppo, non un dato aziendale.
- 183 ispezioni inutili su 720: è il prezzo di un recall più alto.
- Dipendenze fissate a versioni esatte (D-38): `train_baseline.py` produce gli stessi numeri su ogni macchina con Python ≥ 3.12.
