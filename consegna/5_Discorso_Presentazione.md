# Discorso di presentazione · EnerGuard (6-7 minuti)

Testo da leggere o da seguire a voce, allineato alla [scaletta](4_Scaletta_Demo_e_Test.md). Tra parentesi quadre cosa fare sullo schermo. Prima di iniziare: `python prova_test_giuria.py` (9/9) e `./run_dashboard.sh` aperto da almeno 30 secondi.

---

## 0:00-1:00 · Il problema

> Buongiorno. Siamo il team EnerGuard.
>
> Un'azienda elettrica usa un modello per prevedere quali asset della rete si guasteranno nei prossimi trenta giorni: linee ad alta tensione, trasformatori, cabine primarie, turbine eoliche. Per l'AI Act è un sistema **ad alto rischio**, Allegato III: infrastruttura critica, fornitura di elettricità.
>
> Un guasto non previsto su una cabina che alimenta un ospedale non si recupera. Un'ispezione inutile costa qualche ora di lavoro. Il modello è utile, ma **non deve agire da solo**.
>
> Per questo non abbiamo inseguito l'AUC: il modello è quello del kit, 0.868. Abbiamo costruito **il controllo umano intorno al modello**, e lo abbiamo reso misurabile.

[Mostrare il titolo, la coda e la sidebar con lo stato della catena di audit]

> In ogni momento l'operatore vede che cosa sta succedendo, chi deve decidere, e come fermare tutto. La catena di audit qui in basso è integra: lo vedremo tra poco.

---

## 1:00-2:00 · Una decisione, spiegata

[Aprire la card HIC: AST-01148, cabina primaria critica del Sud]

> Prendiamo una decisione vera. Cabina primaria, Sud, utenza critica. Il livello è **HIC**: decide solo l'umano, sempre, qualunque cosa dica il modello.
>
> In cima c'è il riquadro **"In parole semplici"**, pensato per un operatore a fine turno: semaforo rosso, "circa 6 su 10", cosa fare in cinque passi. È generato da regole fisse, non da un LLM: è istantaneo e non può inventare numeri.
>
> C'è un avviso: i dati storici del Sud potrebbero sottostimare i guasti. Ci torneremo.
>
> Lo scenario **"e se..."** è calcolato dal modello: se la vibrazione fosse nella media, il rischio scenderebbe, ma servirebbe comunque un controllo. E qui sotto, **tre asset simili** dello stesso tipo: tutti e tre si sono guastati.
>
> Per l'esperto ci sono i dettagli: i tre fattori SHAP con la loro direzione e una spiegazione scritta da un LLM. La fonte è sempre dichiarata, e se l'LLM non risponde la card resta spiegata con il template.

---

## 2:00-3:00 · L'umano decide davvero

[Scegliere una card HITL. Scrivere "ok" e premere Rifiuta]

> Proviamo a rifiutare con "ok". Il sistema lo respinge: la motivazione deve avere almeno 15 caratteri, e non può essere la copia di una già usata.

[Scrivere una motivazione vera e premere Rifiuta]

> Con una motivazione vera la decisione esce dalla coda e **non viene eseguita**. Nel codice c'è **un solo punto di esecuzione**, `_esegui`, che controlla di nuovo lo stato: una decisione rifiutata, in attesa, sotto stop o HIC non può arrivarci.
>
> Se nessuno risponde entro 30 minuti, la decisione va in escalation: non parte mai in silenzio.

---

## 3:00-3:45 · Fermare il sistema

[Sidebar: ambito `area:Sud+tipo:linea_AT`, motivazione, ATTIVA STOP, Conferma]

> Ora un incidente: letture anomale sulle linee AT del Sud. Fermiamo solo quelle. Un click più una conferma.
>
> Le **8 decisioni** sulle linee AT del Sud sono bloccate, anche quelle già in coda. Il resto continua: la turbina del Sud e la linea del Nord sono ancora lì. Il banner rosso in alto rende lo stop impossibile da ignorare.
>
> Togliere uno stop è più rischioso che metterlo: serve un **secondo operatore**, diverso dal primo. E le decisioni bloccate non ripartono da sole: vanno risottomesse una per una.

---

## 3:45-4:15 · Ricostruire una decisione

[Scheda Audit trail: cercare l'asset rifiutato]

> Un auditor chiede: chi ha deciso, cosa, quando e perché? Qui lo vediamo in pochi secondi, senza aprire il file. Ogni riga del log contiene l'hash della precedente: se qualcuno modifica una motivazione, la catena si rompe e lo vediamo in ogni schermata.

---

## 4:15-5:30 · Il bias che abbiamo trovato

[Scheda Bias & drift]

> La parte più importante. Sud e Isole hanno asset con profili quasi identici: stessa età, stessa manutenzione, stessi sensori. Ma i guasti registrati sono **0.24 contro 0.45**.
>
> La nostra ipotesi è che al Sud i guasti siano **sotto-segnalati**. Il modello lo conferma: è l'unica area dove prevede molto più di quanto viene registrato, con un gap di calibrazione di 0.177.
>
> Un modello non può correggere etichette sbagliate. Quindi abbiamo fatto tre cose:
>
> 1. tolto l'area dal modello, perché faceva da proxy;
> 2. **non** alzato la soglia al Sud: quei "falsi allarmi" potrebbero essere guasti veri;
> 3. un'allerta di calibrazione che **promuove il Sud a supervisione umana**: lì l'AI non esegue mai da sola.

[Mostrare recall con intervallo e tabelle incrociate]

> Poi siamo andati più a fondo. Incrociando area e criticità, il gruppo servito peggio non è il Sud: sono le **utenze standard di Nord e Centro**, con recall 0.65-0.68. E sono anche le aree dove l'AI agiva più spesso da sola.
>
> Così abbiamo aggiunto una regola: dove il recall è basso, anche un'ispezione di routine passa da un umano. I guasti reali eseguiti senza revisione scendono da 6 a 2, al costo di 83 revisioni in più su 720.
>
> E lo diciamo onestamente: con 24-43 guasti per area gli intervalli di confidenza si sovrappongono. Queste differenze sono segnali da sorvegliare, non prove.

[Matrice confidenza × rischio]

> La matrice mostra dove decide l'AI e dove l'umano. Il colore viene dalla stessa regola del codice: il KPI A6 verifica che codice e dichiarazione coincidano, ed è al 100%.

---

## 5:30-6:30 · Cosa non abbiamo risolto

> Chiudiamo con i limiti, perché un limite dichiarato vale più di uno scoperto.
>
> - La sotto-segnalazione al Sud è un'**ipotesi**: serve una verifica sul campo.
> - Al Nord e al Centro circa un guasto su quattro arriva **senza segnali nei sensori**: nessuna soglia lo risolve senza moltiplicare le ispezioni.
> - Abbiamo **più ispezioni inutili**, 182 su 720: è il prezzo di un recall più alto.
> - Il **drift è simulato**: il dataset non ha date.
> - La correzione del bias è affidata all'umano: per questo misuriamo l'override per area e il comportamento di ogni revisore.
> - Due guasti reali nelle Isole sono ancora eseguiti in automatico.
>
> Nel mondo reale il **provider** è chi sviluppa il sistema e risponde di dati, documentazione, logging e progettazione per la supervisione. Il **deployer** è l'operatore di rete che lo usa in control room: deve affidarlo a persone formate, monitorarlo e conservare i log.

---

## 6:30-7:00 · Chiusura

> EnerGuard non rende il modello più intelligente. Rende **visibile, misurabile e interrompibile** ciò che il modello fa, e lascia all'umano le decisioni che contano.
>
> I sei test della giuria li abbiamo già provati: 9 verifiche su 9. Siamo pronti per le vostre domande.

---

## Promemoria per le domande

| Domanda                                | Risposta breve                                                                                                           |
| -------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| Perché non avete migliorato il modello? | La guida lo sconsiglia, e il problema principale è nelle etichette, non nell'algoritmo                                   |
| Perché l'LLM?                          | Solo per i dettagli tecnici, con guardrail e fallback. La parte per tutti è a regole fisse                               |
| Che cosa succede se stacco la rete?    | La card resta spiegata; la fonte dice `template(fallback:...)`                                                           |
| Dov'è l'unico punto di esecuzione?     | `OversightManager._esegui`: due chiamate, HOTL auto-eseguita e revisione approvata o modificata                          |
| Il log si può manomettere?             | Si può modificare, ma non in silenzio: la catena di hash si rompe e la sidebar lo segnala                                |
| Perché non alzate la soglia al Sud?    | I "falsi positivi" del Sud possono essere guasti veri non registrati: alzarla amplificherebbe il bias (recall 0.88 → 0.65) |
