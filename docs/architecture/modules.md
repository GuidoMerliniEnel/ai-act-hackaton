# Modules

## `train_baseline.py`

Trains a `RandomForestClassifier` (300 trees, balanced class weights,
`random_state=0`) on a 70/30 stratified split.

- Decision thresholds per user criticality (`SOGLIE`): standard 0.30,
  high and critical 0.20 ([D-01](../decisions/index.md#d-01), [D-02](../decisions/index.md#d-02)).
- Confidence = `max(p, 1-p)` ([D-07](../decisions/index.md#d-07)).
- Writes `modello.joblib` and `predizioni.csv`, and prints disaggregated metrics.

## `utils_io.py`

- `carica_csv()` reads both the standard CSV and the Italian Excel variant
  (`;` separator, `,` decimal).
- `prepara_feature()` is the single place where features are built for
  training, dashboard and tests. It excludes `area_geografica` from the
  model ([D-03](../decisions/index.md#d-03)).

## `oversight_manager.py`

| Member                 | Responsibility                                                                    |
| ---------------------- | --------------------------------------------------------------------------------- |
| `proponi_azione()`     | Action from risk: ≥ 0.85 reduce load / urgent inspection, ≥ 0.60 maintenance, ≥ 0.10 routine ([D-09](../decisions/index.md#d-09)) |
| `route()`              | Assigns HIC / HITL / HOTL ([D-08](../decisions/index.md#d-08))                    |
| `livello_dichiarato()` | Independent copy of the declared matrix, used for KPI A6                          |
| `sottometti()`         | Routes, then auto-executes (HOTL), queues, or blocks under stop                   |
| `revisiona()`          | Human review with mandatory, non-duplicate justification                          |
| `attiva_stop()` / `disattiva_stop()` | Scoped emergency stop; four-eyes deactivation                       |
| `risottometti()`       | Re-enters a blocked decision as a new one, evaluated from scratch                 |
| `controlla_sla()`      | Moves pending decisions past 30 minutes to `ESCALATION`                           |
| `imposta_promozioni()` | Areas where HOTL is forbidden because of an alert                                 |
| `imposta_vigilanza()`  | Areas with a recall-gap alert: HOTL only below p = 0.10 ([D-39](../decisions/index.md#d-39)) |
| `_esegui()`            | **Only** execution point                                                          |
| `kpi()`                | KPIs A1–A6 and level distribution                                                 |
| `override_per_area()`  | Override rate per area with alert                                                 |

## `bias_detector.py`

| Method                                  | Purpose                                                               |
| --------------------------------------- | --------------------------------------------------------------------- |
| `metriche_per_gruppo()`                 | n, real positives, selection, accuracy, precision, recall, FNR, FPR   |
| `allerte()`                             | Recall gap > 0.15, selection gap > 0.20                               |
| `calibrazione_per_gruppo()`             | Mean predicted probability vs observed rate                           |
| `gruppi_da_promuovere()`                | Groups with calibration gap > 0.10                                    |
| `gruppi_recall_basso()`                 | Groups with recall gap > 0.15, watched by the routing (D-39)          |
| `recall_con_intervallo()`               | Recall with 95% bootstrap interval per group (D-40)                   |
| `metriche_incrociate()`                 | Recall, FPR and calibration for two crossed groups, n ≥ 15 (D-41)     |
| `drift_settimanale()` / `allerta_drift()` | 12 simulated weeks; alert after 2 consecutive weeks below reference − 0.10 |

## `explainer.py`

- `estrai_fattori()` computes the top three SHAP factors and puts
  risk-increasing factors first ([D-22](../decisions/index.md#d-22)). It
  labels values against fleet percentiles ([D-21](../decisions/index.md#d-21)).
- `SpiegatoreTemplate` builds a deterministic explanation.
- `SpiegatoreLLM` calls the configured provider, applies guardrails, and
  falls back to the template.
- `crea_spiegatore()` picks the engine from `.env`.

## `audit_logger.py`

Append-only JSONL. Each record holds the hash of the previous record, so
any later edit breaks the chain. `verifica_catena()` returns integrity and
record count. Writes are protected by a lock because explanations are
generated in parallel ([D-24](../decisions/index.md#d-24)).

## `app.py`

Streamlit dashboard: bootstrap, sidebar with stop and integrity indicator,
and five tabs. See [Using the Dashboard](../getting-started/usage.md).
