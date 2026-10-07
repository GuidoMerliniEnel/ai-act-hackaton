# Oversight KPIs

A system that does not measure its own supervision cannot be supervised.
These KPIs are computed by `OversightManager.kpi()`, `BiasDetector` and
`AuditLogger`, and shown in the dashboard.

## A. Effectiveness of oversight

| #  | Indicator                          | Formula                                                    | Target        | Alarm signal |
| -- | ---------------------------------- | ---------------------------------------------------------- | ------------- | ------------ |
| A1 | Improper auto-execution            | HIC/HITL executed without human review                     | **0**         | Any value > 0 |
| A2 | Human override rate                | (rejected + modified) / reviewed                           | 5% – 40%      | ~0% rubber-stamping; > 60% model unusable |
| A3 | Median review time                 | median(closed − opened)                                    | 30 s – 5 min  | < 10 s systematic; monitored per reviewer ([D-40](../decisions/index.md#d-40)) |
| A4 | Rubber-stamping index              | % reviews with justification < 30 chars or duplicate       | < 10%         | > 30% |
| A5 | SLA escalation rate                | expired / HITL decisions                                   | < 15%         | Human queue undersized |
| A6 | Declared routing coverage          | % decisions whose level matches the declared matrix        | **100%**      | Code does not do what the document promises |

## B. Understandability and transparency

| #   | Indicator                     | Target | How EnerGuard meets it |
| --- | ----------------------------- | ------ | ---------------------- |
| B1  | Explanation coverage (≥ 3 factors) | 100% | Three factors always listed under each card |
| B2  | Uncertainty visibility        | 100%   | Confidence and an uncertainty note on every card |
| B3  | 60-second test                | Pass   | See [T4](verification-tests.md#t4) |
| B3b | Explanation source declared   | 100%   | `template`, `llm:…` or `template(fallback:…)`, logged |
| B3c | LLM fallback rate             | < 5%   | 0/10 in the demo with `max_completion_tokens` 2000 |
| B4  | Clicks to explanation / override / stop | ≤ 2 / ≤ 2 / ≤ 1 | Explanation on the card; buttons on the card; stop in the sidebar |

## C. Fairness and continuous monitoring

| #  | Indicator                    | Target                     | Current value |
| -- | ---------------------------- | -------------------------- | ------------- |
| C1 | Max recall gap               | Measured; alert > 0.15     | 0.216 by area (North; 95% CI 0.57–0.89 vs Islands 0.84–1.00) — alert, North and Centre watched (D-43) |
| C2 | Calibration gap per group    | Alert > 0.10               | South 0.177 — alert, area promoted to HITL |
| C3 | Override rate per area       | Exposed                    | Alert at > 2× average with ≥ 3 reviews |
| C4 | Performance drift            | Chart + alert threshold    | 12 simulated weeks; no alert on current data |

## D. Traceability

| #  | Indicator               | Target                          | How EnerGuard meets it |
| -- | ----------------------- | ------------------------------- | ---------------------- |
| D1 | Audit trail completeness | 100% of transitions logged     | Queue entry, HOTL auto-execution, review, escalation, stop on/off, block, resubmission, promotion, LLM calls |
| D2 | Log integrity           | Verifiable from the dashboard   | SHA-256 hash chain, status in the sidebar |
| D3 | Decision reconstruction | < 60 s                          | Audit tab: search by asset ID |
