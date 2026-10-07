# Discorso di presentazione · EnerGuard (6-7 minuti)

Testo da leggere o da seguire a voce, allineato alla [scaletta](4_Scaletta_Demo_e_Test.md) e alla struttura chiesta dalla giuria: **1' scenario, 3' il percorso di UNA decisione, 2' bias, limiti e trade-off**. Tra parentesi quadre cosa fare sullo schermo; a margine il tier e il requisito coperti. Prima di iniziare: `python prova_test_giuria.py` (10/10) e `./run_dashboard.sh` aperto da almeno 30 secondi.

---

## 0:00-1:00 · Lo scenario (per l'operatore, non per il data scientist)

> Buongiorno, siamo il team EnerGuard.
>
> Un modello prevede quali asset della rete elettrica si guasteranno entro trenta giorni: linee ad alta tensione, trasformatori, cabine primarie, turbine eoliche. Per l'AI Act è un sistema **ad alto rischio**, Allegato III: infrastruttura critica.
>
> Un guasto mancato su una cabina che alimenta un ospedale non si recupera; un'ispezione inutile costa qualche ora. Per questo abbiamo scelto la soglia di intervento in base ai costi: **0.30 per le utenze standard e 0.20 per quelle alte e critiche**, assumendo che un guasto mancato costi dieci volte un'ispezione inutile. Il modello è quello del kit, AUC 0.868: non abbiamo inseguito l'accuratezza, abbiamo costruito un sistema che un operatore può **capire, monitorare, correggere e fermare**.

[Mostrare la barra dei KPI in alto e la sidebar]

> Qui in alto l'operatore vede sempre lo stato: decisioni in attesa, override, copertura delle spiegazioni, allerte di fairness e integrità del log.

*Tier 1 (soglia giustificata) · Art. 14: capire e monitorare · KPI in dashboard*

---

## 1:00-4:00 · Il percorso di UNA decisione

### Predizione e routing

[Aprire la card AST-01148]

> Seguiamo una sola decisione, dall'inizio alla fine. **AST-01148**: cabina primaria del Sud che alimenta un'utenza critica. Il modello stima circa 6 probabilità su 10 di guasto, con confidenza 0.65.
>
> Il routing applica una matrice dichiarata. **HIC** per le utenze critiche: decide solo l'umano, sempre. **HITL** se il rischio supera 0.60 o la confidenza è sotto 0.80. **HOTL**, cioè l'AI agisce da sola, solo per azioni di routine con rischio sotto 0.20. Questa decisione è HIC.

*Tier 2A (matrice di routing con soglie)*

### Spiegazione e incertezza

> In cima c'è il riquadro **"In parole semplici"**: semaforo, "circa 6 su 10", cosa fare. Il motivo principale: vibrazione a 8.7, molto sopra la norma, e 451 giorni senza manutenzione. L'**incertezza è dichiarata**: con confidenza 0.65 il sistema dice apertamente di non essere sicuro.
>
> Lo scenario **"e se..."** è calcolato dal modello: con la vibrazione nella media il rischio scenderebbe a 3 su 10, ma servirebbe comunque un controllo. E i **tre asset più simili** dello stesso tipo si sono guastati tutti e tre.
>
> I dettagli per l'esperto mostrano i tre fattori con la loro direzione e la **fonte** della spiegazione: oggi il template; con l'LLM attivo resta lo stesso schema, con guardrail e ritorno automatico al template.

*Tier 3A (spiegabilità, incertezza visibile) · test T4*

### Giudizio umano

[Scrivere "ok" e premere Rifiuta]

> Il revisore ha quattro azioni: **approva, modifica, rifiuta, escalation**. Proviamo a rifiutare con "ok": respinto. La motivazione deve avere almeno 15 caratteri e non può essere la copia di una già usata.

[Scrivere "Sopralluogo di ieri: vibrazione nella norma, sensore da ricalibrare" e premere Rifiuta]

> Con una motivazione vera la decisione esce dalla coda e **non viene eseguita**. Nel codice c'è **un solo punto di esecuzione**, `_esegui`: una decisione rifiutata, in attesa, sotto stop o HIC non può arrivarci. Se nessuno decide entro 30 minuti, va in escalation: mai eseguita in silenzio.

*Tier 2B (coda, motivazione, SLA) · test T1, T2*

### Audit trail

[Scheda Audit trail: cercare AST-01148]

> Chi ha deciso, cosa, quando e perché: lo ricostruiamo in pochi secondi, senza aprire il file. Ogni riga contiene l'hash della precedente: se qualcuno modifica una motivazione, la catena si rompe e lo vediamo in ogni schermata.

*Tier 3C (audit filtrabile, integrità) · test T6*

### Fermare il sistema

[Sidebar: ambito `area:Sud+tipo:linea_AT`, motivazione, ATTIVA STOP, Conferma]

> Ultimo passo: un incidente sulle linee AT del Sud. Lo stop funziona **globale, per area, per tipo di asset o combinato**. Fermiamo solo queste: un click più una conferma. Le **7 decisioni** in coda sono bloccate, il resto continua, il banner rosso lo segnala. Per togliere lo stop serve un **secondo operatore**, e le decisioni bloccate non ripartono da sole.

*Tier 2C (emergency stop) · test T3*

---

## 4:00-6:30 · Bias, limiti, trade-off

[Scheda Bias & drift]

> Le metriche aggregate mentono, quindi le abbiamo divise per area e per tipo di asset. Sud e Isole hanno asset quasi identici per età, manutenzione e sensori, ma guasti registrati **0.24 contro 0.45**. Due ipotesi: i guasti del Sud sono **sotto-segnalati**, oppure i **processi di registrazione** sono diversi tra territori. I dati non le distinguono, ma la calibrazione indica la prima: il Sud è l'unica area dove il modello prevede molto più di quanto viene registrato.
>
> Abbiamo tolto l'area dal modello perché faceva da proxy, e **non** abbiamo alzato la soglia al Sud, perché quei "falsi allarmi" potrebbero essere guasti veri. Poi un'**allerta che agisce**: oltre 0.10 di gap di calibrazione le decisioni dell'area passano a supervisione umana. Al Sud l'AI non esegue mai da sola.

[Mostrare recall con intervallo, tabelle incrociate, drift e override per area]

> Incrociando area e criticità, il gruppo servito peggio sono le **utenze standard di Nord e Centro**, recall 0.65-0.68. Lì ora anche l'ispezione di routine passa da un umano: i guasti reali eseguiti senza revisione scendono da 6 a 2, al costo di 83 revisioni in più su 720.
>
> Il monitoraggio è continuo: accuratezza e confidenza su dodici settimane simulate, con un'allerta che spegne l'automazione se l'accuratezza cala due settimane di fila. In più il tasso di override per area e per revisore, per accorgerci di chi approva senza leggere.

[Matrice confidenza × rischio]

> La matrice mostra dove decide l'AI e dove l'umano, con lo stesso codice della dichiarazione: il KPI A6 è al 100%.

*Tier 1 (metriche disaggregate, due ipotesi) · Tier 3B (bias, drift, override, alert) · test T5*

> Ora i limiti, perché un limite dichiarato vale più di uno scoperto:
>
> - la sotto-segnalazione è un'**ipotesi** da verificare sul campo;
> - al Nord e al Centro un guasto su quattro arriva **senza segnali nei sensori**;
> - **182 ispezioni inutili** su 720, il prezzo di un recall più alto;
> - con 24-43 guasti per area le differenze sono **segnali, non prove**;
> - il **drift è simulato** e due guasti nelle Isole restano automatici.
>
> Tutto è nella **model card**, nella **relazione d'impatto** e nella **dichiarazione di oversight**. Nel mondo reale il **provider** è chi sviluppa il sistema e risponde di dati, documentazione, logging e progettazione della supervisione; il **deployer** è l'operatore di rete, che deve affidarlo a persone formate, monitorarlo e conservare i log.

*Tier 4 (documenti, limiti, provider e deployer)*

---

## 6:30-7:00 · Chiusura

> In un'infrastruttura critica un sistema accurato ma non supervisionabile è pericoloso. EnerGuard lascia all'umano le decisioni che contano, e lo rende misurabile: abbiamo già provato i sei test della giuria, dieci verifiche su dieci. Siamo pronti per le vostre domande.

---

## Copertura delle richieste della giuria

| Richiesta (slide)                                   | Dove nel discorso                    |
| --------------------------------------------------- | ------------------------------------ |
| Tier 1: baseline, soglia giustificata               | Scenario                             |
| Tier 1: metriche disaggregate, ≥ 2 ipotesi Sud/Isole | Bias, limiti, trade-off              |
| Tier 2A: matrice HIC/HITL/HOTL con soglie           | Predizione e routing                 |
| Tier 2B: 4 azioni, motivazione, SLA, punto unico    | Giudizio umano                       |
| Tier 2C: stop a tre granularità, coda, log          | Fermare il sistema                   |
| Tier 3A: 3 fattori, linguaggio operativo, incertezza | Spiegazione e incertezza            |
| Tier 3B: bias, calibrazione, drift, override        | Bias, limiti, trade-off              |
| Tier 3C: alert che agiscono, audit con integrità    | Audit trail; allerta di calibrazione |
| Tier 4: scaletta 1' + 3' + 2', documenti, limiti    | Struttura del discorso; limiti       |
| Provider e deployer                                 | Limiti                               |
| Sei test T1-T6                                      | Indicati a margine di ogni passo     |

## Promemoria per le domande

| Domanda                                 | Risposta breve                                                                                                             |
| --------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| Perché non avete migliorato il modello? | La guida lo sconsiglia, e il problema principale è nelle etichette, non nell'algoritmo                                     |
| Perché l'LLM?                           | Solo per i dettagli tecnici, con guardrail e fallback. La parte per tutti è a regole fisse                                 |
| Che cosa succede se stacco la rete?     | La card resta spiegata; la fonte dice `template(fallback:...)`                                                             |
| Dov'è l'unico punto di esecuzione?      | `OversightManager._esegui`: due chiamate, HOTL auto-eseguita e revisione approvata o modificata                            |
| Il log si può manomettere?              | Si può modificare, ma non in silenzio: la catena di hash si rompe e la barra in alto lo segnala                            |
| Perché non alzate la soglia al Sud?     | I "falsi positivi" del Sud possono essere guasti veri non registrati: alzarla amplificherebbe il bias (recall 0.88 → 0.65) |
| Perché 0.30 e 0.20?                     | Costo 10:1 tra guasto mancato e ispezione inutile; 0.20 ovunque avrebbe saturato la coda umana (230 ispezioni inutili)     |
