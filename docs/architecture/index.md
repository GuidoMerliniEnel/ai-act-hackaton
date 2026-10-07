# Architecture

EnerGuard is a single-process Python application. The model produces
predictions offline. The dashboard loads them, routes each recommendation
through the oversight manager, and records every transition in an
append-only, hash-chained log.

```mermaid
flowchart TB
    subgraph Offline
        DS[(energuard_dataset.csv)] --> TB[train_baseline.py<br/>RandomForest + SOGLIE]
        TB --> M[(modello.joblib)]
        TB --> P[(predizioni.csv)]
    end

    subgraph Dashboard["app.py (Streamlit)"]
        P --> BD[BiasDetector<br/>calibration · drift]
        BD -->|promoted areas| OM
        P --> PA[proponi_azione]
        PA --> OM[OversightManager<br/>route · queue · stop · SLA]
        M --> EX[Explainer<br/>SHAP → template / LLM]
        EX --> UI[Decision cards]
        OM --> UI
        UI -->|approve / modify / reject| OM
        OM -->|only path| EXE[_esegui]
    end

    OM --> AL[AuditLogger]
    EX --> AL
    AL --> LOG[(audit_trail.jsonl<br/>hash chain)]
```

## Decision lifecycle

```mermaid
stateDiagram-v2
    [*] --> Routed: sottometti()
    Routed --> AUTO_ESEGUITA: HOTL
    Routed --> IN_ATTESA: HIC / HITL
    Routed --> BLOCCATA_STOP: stop active
    IN_ATTESA --> APPROVATA: review + justification
    IN_ATTESA --> MODIFICATA: review + justification
    IN_ATTESA --> RIFIUTATA: review + justification
    IN_ATTESA --> ESCALATION: SLA expired / manual
    IN_ATTESA --> BLOCCATA_STOP: stop activated
    ESCALATION --> APPROVATA
    ESCALATION --> MODIFICATA
    ESCALATION --> RIFIUTATA
    ESCALATION --> BLOCCATA_STOP
    BLOCCATA_STOP --> RISOTTOMESSA: resubmission after unlock
    RISOTTOMESSA --> [*]: new decision re-routed
    APPROVATA --> [*]: _esegui
    MODIFICATA --> [*]: _esegui
    AUTO_ESEGUITA --> [*]: _esegui
    RIFIUTATA --> [*]
```

Only `APPROVATA`, `MODIFICATA` and `AUTO_ESEGUITA` (HOTL only) reach
`_esegui`. The method also asserts that the decision is not HIC
auto-executed and is not under an active stop
([D-10](../decisions/index.md#d-10)).

## Design principles

| Principle                  | Implementation                                                         |
| -------------------------- | ---------------------------------------------------------------------- |
| Single execution point     | `OversightManager._esegui` with state, level and stop assertions       |
| Declared = implemented     | `route()` and an independent `livello_dichiarato()`; KPI A6 compares them |
| Everything is logged       | `AuditLogger.log` on every transition, thread-safe                     |
| Tamper evidence            | SHA-256 hash chain verified on every page load                         |
| The LLM does not decide    | Numbers come from the model; the LLM only rephrases, with guardrails   |
| Bias handled by oversight  | Calibration alert promotes an area to HITL rather than retuning labels |

See [Modules](modules.md) and [Dataset](dataset.md) for details.
