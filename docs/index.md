---
hide:
  - toc
---

# EnerGuard

**Human oversight for predictive maintenance of grid assets**, designed
for the EU AI Act requirements on high-risk systems (Annex III, critical
infrastructure).

A random-forest model predicts which assets (HV lines, transformers,
primary substations, wind turbines) are likely to fail within 30 days.
EnerGuard puts a supervision layer around it. Each recommendation is
routed to the right level of human control. Every human decision needs a
justification. Operators can stop the system, fully or partially, with
one click. Every step is recorded in a tamper-evident log.

---

<div class="grid cards" markdown>

- :material-rocket-launch:{ .lg .middle } **Getting Started**

  ***

  Install, train the model, run the dashboard and configure the LLM
  explanation engine.

  [:octicons-arrow-right-24: Getting Started](getting-started/index.md)

- :material-sitemap:{ .lg .middle } **Architecture**

  ***

  How the model, the oversight manager, the bias detector, the explainer
  and the audit trail fit together.

  [:octicons-arrow-right-24: Architecture](architecture/index.md)

- :material-scale-balance:{ .lg .middle } **Compliance**

  ***

  Model card, impact assessment and oversight declaration: the three
  documents required by the AI Act and by the hackathon.

  [:octicons-arrow-right-24: Compliance](compliance/index.md)

- :material-gauge:{ .lg .middle } **Quality**

  ***

  Oversight KPIs A1–A6 measured by the system itself, and the six live
  verification tests T1–T6.

  [:octicons-arrow-right-24: Quality](quality/index.md)

- :material-file-document-edit:{ .lg .middle } **Decisions**

  ***

  The 37 design decisions (D-01..D-37), with rationale and where they
  live in the code.

  [:octicons-arrow-right-24: Decisions](decisions/index.md)

- :material-source-branch:{ .lg .middle } **Project**

  ***

  Contributing, security policy and license, following the Enel OSPO
  guidelines.

  [:octicons-arrow-right-24: Contributing](project/contributing.md)

</div>

---

<!-- prettier-ignore-start -->
!!! info "Five questions in a few seconds"

    The dashboard is designed so that an operator can answer, at any time:

    1. **What is happening?** Queue, levels, active stops.
    2. **Why does the system recommend this?** Explanation in operational language.
    3. **How much can I trust it, here and now?** Confidence, uncertainty, recent performance.
    4. **What can I do?** Approve, modify, reject, escalate.
    5. **How do I stop it?** Global or partial emergency stop, one click away.
<!-- prettier-ignore-end -->
