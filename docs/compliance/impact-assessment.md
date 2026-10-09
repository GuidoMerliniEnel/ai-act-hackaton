# Impact Assessment

## Risks identified

| ID  | Risk                                                                                | Severity | Evidence                                                                                              |
| --- | ----------------------------------------------------------------------------------- | -------- | ----------------------------------------------------------------------------------------------------- |
| R1  | Missed failure on a critical user (hospital, infrastructure)                        | Critical | 3 FN on critical and 6 on high users with a single 0.30 threshold                                     |
| R2  | Historical label bias: failures under-reported in the South                         | High     | South/Islands same profile, 0.24 vs 0.45 recorded; South calibration gap 0.177                        |
| R3  | Area acting as a proxy, causing over-selection in South and Islands                 | Medium   | Selection gap 0.64 between areas; FPR Islands 0.67 with area in the model                             |
| R4  | Lower recall in North and Centre                                                    | Medium   | Recall 0.54 (Centre) with area in the model                                                           |
| R5  | Automation bias: operators approve without reading                                  | High     | General risk of approval queues                                                                       |
| R6  | Oversight on paper only: actions executed despite rejection, pending status or stop | Critical | Typical failure checked by tests T1 and T3                                                            |
| R7  | Audit trail edited without detection                                                | High     | Plain JSONL is editable                                                                               |
| R8  | LLM invents numbers or is unavailable                                               | Medium   | Empty responses observed with 400 output tokens                                                       |
| R9  | Performance drift over time                                                         | Medium   | Weekly accuracy oscillates ±0.08                                                                      |
| R10 | Missed failures concentrated where the AI acts alone                                | High     | North/Centre: lowest recall and 70%/53% auto-execution; 6 real failures auto-executed on the test set |

## Mitigations implemented

| Risk | Mitigation                                                                                                           | Measured effect                                              |
| ---- | -------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------ |
| R1   | Threshold 0.20 for high/critical users; HIC for every critical user                                                  | FN critical/high 3/6 → 1/1                                   |
| R2   | Calibration alert > 0.10 promotes the area from HOTL to HITL                                                         | South promoted; no auto-execution in the South               |
| R3   | `area_geografica` removed from the model                                                                             | AUC 0.862 → 0.868; FPR Islands 0.667 → 0.622                 |
| R4   | Removing area plus differentiated thresholds                                                                         | Recall gap 0.411 → 0.216; Centre 0.542 → 0.750               |
| R5   | Justification ≥ 15 chars, duplicates rejected, rubber-stamping index A4, review time A3                              | Measured live in the KPI tab                                 |
| R6   | Single execution point with assertions; stop also freezes the existing queue                                         | Tests T1, T3 passed                                          |
| R7   | SHA-256 hash chain, integrity always visible                                                                         | Edit at record 403 detected (test T6)                        |
| R8   | Guardrails, template fallback, declared source                                                                       | 10/10 LLM explanations, 0 fallbacks in the demo              |
| R9   | Drift alert: 2 consecutive weeks below reference − 0.10 disables HOTL everywhere                                     | Triggers in simulation; not on current data                  |
| R10  | Recall-gap alert: no auto-execution above p = 0.10 in the area; recall CI and intersectional tables in the dashboard | Real failures auto-executed 6 → 2; +84 HITL decisions on 720 |

**Cost of the mitigation package:** 30 more unnecessary inspections
(153 → 183) for 5 fewer missed failures (26 → 21), consistent with the
declared 10:1 cost ratio.

## What we have NOT solved

!!! danger "Open issues" 1. **The label bias in the South is managed, not removed.** Removing
the area made the South calibration gap slightly worse
(0.159 → 0.177), because age and maintenance history act as proxies.
Only a field check of recording practices can confirm or rule out
under-reporting. 2. **We cannot tell under-reporting from different recording processes.**
Both hypotheses fit the data. 3. **Recall gap in the North (0.216) is still above the 0.15 alert.**
These failures have no sensor signal; lowering the threshold would
flood the queue (230 FP at 0.20). 4. **The 10:1 cost ratio is an assumption**, not measured on real
incidents. 5. **Confidence `max(p, 1-p)` is not an independent uncertainty
measure.** HOTL effectively requires p ≤ 0.20. 6. **The justification checks are proxies.** A long, unique but
meaningless text passes. A4 measures the symptom, not the quality. 7. **Drift is simulated** on test-set blocks; there is no real time axis. 8. **Operator identity is self-declared** in the sidebar, with no
authentication. The four-eyes rule on stop deactivation relies on it. 9. **State is in memory.** The queue resets when the dashboard restarts;
only the audit trail persists. 10. **The LLM depends on an external provider**, which adds
non-determinism. Fallback keeps the dashboard working, but wording
may differ between runs. 11. **Standard users in North and Centre are served worst** (recall
0.65–0.68). D-43 adds oversight, not recall. 12. **Area still leaks in indirectly**: age and days since maintenance
predict it 58% of the time. We keep them because they are real risk
factors. 13. **Per-area differences are not statistically solid**: 24–43
failures per area, overlapping confidence intervals. 14. **Two real failures in the Islands are still auto-executed**
(risk 0.14–0.17), an area with no alert. D-43 also adds 84 HITL
decisions on 720: KPI A5 must be watched. 15. **The calibration alert uses absolute points, not proportions.**
The model over-predicts almost everywhere (25 vs 18 failures per 100,
an effect of balanced class weights). Recorded failures per 100
expected: North 60, Centre 67, South 57, Islands 107. Only the South
exceeds the 0.10 gap (0.177), but in proportion the North is close and
may hide under-recording behind its low base rate. The strongest
evidence of the South bias remains the direct comparison with the
Islands in the data.
