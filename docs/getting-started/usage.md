# Using the Dashboard

The dashboard has a sidebar that is always visible and five tabs.

## Sidebar

| Element                | Purpose                                                                                  |
| ---------------------- | ---------------------------------------------------------------------------------------- |
| **Operator ID**        | Pseudonymous identifier recorded in the audit trail for every human action               |
| **Explanation engine** | Shows whether explanations come from the template or an LLM                              |
| **Emergency stop**     | Scope selector, mandatory justification, **ATTIVA STOP** plus confirmation               |
| **Active stops**       | List of active stops and deactivation, which needs a second operator ([D-15](../decisions/index.md#d-15)) |
| **Audit trail status** | Hash-chain integrity and record count, always visible ([D-30](../decisions/index.md#d-30)) |

Stop scopes: `GLOBALE`, one area (`area:Sud`), one asset type
(`tipo:linea_AT`), or a combination such as `area:Sud+tipo:linea_AT`
([D-13](../decisions/index.md#d-13)).

## Tabs

### Decision queue (*Coda decisioni*)

Each card shows the asset, the recommended action, the oversight level,
the failure probability and the confidence. It also shows an explanation in
plain language with the three main factors and their direction
([D-23](../decisions/index.md#d-23)).

Actions: **Approve**, **Modify**, **Reject**, **Escalation**. Each needs a
justification of at least 15 characters. Copy-pasted justifications are
rejected ([D-11](../decisions/index.md#d-11)).

Decisions blocked by a stop appear in a separate *Blocked* section. They
return to the flow only after an explicit resubmission
([D-16](../decisions/index.md#d-16)).

### Confidence × risk matrix

Every test-set decision is plotted by probability and confidence. Points
are colored by the level from the declared matrix, with the routing
thresholds drawn as dashed lines ([D-25](../decisions/index.md#d-25)).

### Bias & drift

- Disaggregated metrics by area and asset type, with recall-gap alerts.
- Calibration per area. Areas above the 0.10 gap are promoted from HOTL to
  HITL ([D-19](../decisions/index.md#d-19)).
- Accuracy, recall and mean confidence over 12 simulated weeks, with a
  drift alert ([D-26](../decisions/index.md#d-26), [D-27](../decisions/index.md#d-27)).
- Override rate per area, with an alert at twice the average
  ([D-28](../decisions/index.md#d-28)).

### Audit trail

Reconstruct a decision by asset ID: who, what, when, why, and whether the
AI was approved or corrected. You can filter the log by asset, actor and
period, and export it to CSV or JSONL ([D-29](../decisions/index.md#d-29)).

### Oversight KPIs

KPIs A1–A6 with targets and the distribution of levels. See
[Oversight KPIs](../quality/kpis.md).
