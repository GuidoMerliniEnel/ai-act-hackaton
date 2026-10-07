# Dichiarazione di oversight · EnerGuard

Regole applicate in ordine, vale la prima che scatta. Implementate in `OversightManager.route()` e, in copia indipendente, in `livello_dichiarato()`: il KPI A6 verifica che coincidano (100%).

| #   | Condizione                                                   | Livello  | Perché                                                         |
| --- | ------------------------------------------------------------ | -------- | -------------------------------------------------------------- |
| 1   | Utenza **critica**                                           | **HIC**  | Errore irreversibile (ospedali): decide solo l'umano           |
| 2   | **Riduzione del carico** su utenza **alta**                  | **HIC**  | Effetto diretto sulle persone servite                          |
| 3   | Probabilità **≥ 0.60** o confidenza **< 0.80**               | **HITL** | Rischio alto o modello incerto                                 |
| 4   | Area con **allerta di calibrazione o drift**                 | **HITL** | Dati sospetti: niente auto-esecuzione (D-19, D-27)             |
| 5   | Area con **allerta di recall** e probabilità **≥ 0.10**      | **HITL** | Dove il modello manca più guasti, rivede l'umano (D-43)        |
| 6   | Azione leggera (nessuna azione, ispezione di routine)        | **HOTL** | Costo basso e reversibile: il sistema agisce, l'umano monitora |
| 7   | Tutto il resto                                               | **HITL** | Default prudente                                               |

**Soglie.** 0.60 e 0.80 sono i default del kit, mantenuti: con confidenza = max(p, 1−p) una decisione va in HOTL solo se p ≤ 0.20. Le allerte scattano oltre 0.10 di gap di calibrazione e 0.15 di gap di recall. Sul test set: 60 HIC, 422 HITL, 238 HOTL.

**Flusso umano.** Motivazione ≥ 15 caratteri e non fotocopia; SLA di 30 minuti, poi escalation; un solo punto di esecuzione; stop globale, per area, per tipo o combinato, anche sulla coda esistente; sblocco con secondo operatore. Dettagli: [allegato](6_Allegato_Versione_Estesa.md).

**Provider e deployer.** Il **provider** è chi sviluppa il sistema (unità IT/data o fornitore): governance dei dati, documentazione tecnica, logging, trasparenza verso il deployer, progettazione per la supervisione (Art. 10-15). Il **deployer** è l'operatore di rete che lo usa in control room: supervisione affidata a persone formate, uso secondo le istruzioni, monitoraggio, conservazione dei log, segnalazione di incidenti (Art. 26).
