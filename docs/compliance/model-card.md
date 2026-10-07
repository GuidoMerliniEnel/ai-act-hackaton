# Model Card

<!-- prettier-ignore-start -->
!!! note "Official deliverable"

    The official, Italian model card handed in for the hackathon is
    `consegna/1_Model_Card.md`. This page is the English summary; numbers
    come from the same `predizioni.csv`.
<!-- prettier-ignore-end -->

## Purpose

Predict the probability that a grid asset fails **within 30 days**, so that
inspections and maintenance can be prioritised. The model **recommends**.
Every recommendation goes through the human-oversight layer, and no
critical-user action is ever taken without a human decision.

**Intended users:** control-room operators of an electricity distribution
company. **Out of scope:** automatic switching or load shedding without
human approval, use on asset types not in the training data, use on real
data without re-validation.

## Data

- Synthetic dataset, 2,400 assets, 12 columns
  ([details](../architecture/dataset.md)).
- 70/30 stratified split (`random_state=0`); test set of 720 assets.
- `area_geografica` is **excluded from the model** because it acts as a
  proxy for label bias. It is kept for monitoring, stops and fairness
  ([D-03](../decisions/index.md#d-03)).

## Model

| Item               | Value                                                                                                                                                                                                                                                                            |
| ------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Algorithm          | Random forest, 300 trees, balanced class weights                                                                                                                                                                                                                                 |
| Features           | Asset type, age, temperature, vibration, load, humidity, maintenance count, days since last maintenance, user criticality                                                                                                                                                        |
| Decision threshold | 0.30 for standard users; 0.20 for high and critical users ([D-01](../decisions/index.md#d-01), [D-02](../decisions/index.md#d-02))                                                                                                                                               |
| Cost assumption    | A missed failure costs about 10 times an unnecessary inspection (declared hypothesis)                                                                                                                                                                                            |
| Confidence         | `max(p, 1-p)` ([D-07](../decisions/index.md#d-07))                                                                                                                                                                                                                               |
| Explanations       | Plain-language box by fixed rules with a computed "what if" scenario ([D-31](../decisions/index.md#d-31)..[D-34](../decisions/index.md#d-34)); expert details: top three SHAP factors rendered by LLM with guardrails and template fallback ([D-20](../decisions/index.md#d-20)) |

## Global metrics (test set, 720 assets)

| Metric                       | Value                   |
| ---------------------------- | ----------------------- |
| AUC                          | 0.868                   |
| Recall                       | 0.837                   |
| Precision                    | 0.371                   |
| Accuracy                     | 0.717                   |
| Missed failures (FN)         | 21 (1 critical, 1 high) |
| Unnecessary inspections (FP) | 183                     |

## Metrics by subgroup

### By area (not a model feature)

| Area   | n   | Real failures | Selection | Recall | FPR   | Calibration gap |
| ------ | --- | ------------- | --------- | ------ | ----- | --------------- |
| Nord   | 300 | 0.093         | 0.200     | 0.714  | 0.147 | 0.062           |
| Centro | 189 | 0.127         | 0.307     | 0.750  | 0.242 | 0.064           |
| Sud    | 143 | 0.238         | 0.734     | 0.882  | 0.688 | **0.177**       |
| Isole  | 88  | 0.489         | 0.773     | 0.930  | 0.622 | −0.034          |

Calibration gap = mean predicted probability − observed failure rate.
Alert threshold: 0.10.

### By asset type

| Asset type      | n   | Recall | FPR   |
| --------------- | --- | ------ | ----- |
| cabina_primaria | 135 | 0.810  | 0.333 |
| trasformatore   | 271 | 0.814  | 0.333 |
| linea_AT        | 171 | 0.824  | 0.307 |
| turbina_eolica  | 143 | 0.903  | 0.241 |

### By user criticality

| Criticality | n   | Recall | FPR   |
| ----------- | --- | ------ | ----- |
| standard    | 462 | 0.765  | 0.252 |
| alta        | 198 | 0.971  | 0.421 |
| critica     | 60  | 0.929  | 0.391 |

## Known limitations

<!-- prettier-ignore-start -->
!!! warning "Declared limits"

    - **Recall gap North (0.216 > 0.15).** Missed failures in the North and
      Centre show no sensor signal (mean vibration 2.8 vs 4.6). The model is
      well calibrated there, so this is a model limit, not label bias
      ([D-06](../decisions/index.md#d-06)).
    - **South calibration gap (0.177).** Probably caused by under-reported
      failures. It cannot be fixed in the model because the bias is in the
      labels; it is managed by oversight, and South decisions are promoted
      to HITL ([D-19](../decisions/index.md#d-19)).
    - **High false-positive rate in South and Islands** (0.69 and 0.62).
      In the South many "false positives" may be real, unrecorded failures
      ([D-05](../decisions/index.md#d-05)).
    - **Confidence adds little information.** With `max(p, 1-p)` the
      points lie on a V and confidence is a function of probability. A
      measure such as tree agreement would be more informative.
    - **Recall gap by criticality (standard 0.765 vs high 0.971)** is
      intentional: it comes from the lower threshold on high and critical
      users.
    - **Simulated drift.** The dataset has no dates; drift is measured on
      12 consecutive blocks of the test set ([D-26](../decisions/index.md#d-26)).
    - **`riduci_carico` is never proposed** in the demo sample (maximum
      probability 0.79 < 0.85), so HIC is triggered only by critical users.
    - **LLM explanations** are non-deterministic and depend on an external
      provider. Guardrails and template fallback mitigate this, but wording
      can vary between runs.
    - **Synthetic data.** Metrics are not representative of a real grid.
<!-- prettier-ignore-end -->

## AI Act risk classification

**High risk**, Annex III point 2 (critical infrastructure: electricity
supply). See [Compliance](index.md).
