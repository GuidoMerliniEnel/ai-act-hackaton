# Quality

A supervision dashboard is good if, and only if, it lets an operator
answer five questions in a few seconds: what is happening, why, how much
to trust it, what can I do, and how do I stop it.

Quality is measured on three layers:

1. **[Oversight KPIs](kpis.md)** measured by the system itself and shown
   in the dashboard.
2. **[Verification tests](verification-tests.md)** T1–T6, run live by the
   jury.
3. **Qualitative rubric** (1–4 per dimension: human intervention,
   understandability, fairness, traceability).

## Automated quality gates (CI)

| Gate            | Tool                                     | Workflow                     |
| --------------- | ---------------------------------------- | ---------------------------- |
| Syntax          | `python -m compileall`                   | `.github/workflows/ci.yml`   |
| Model & fairness | `python train_baseline.py`              | `.github/workflows/ci.yml`   |
| Explanations    | `python test_llm.py` (template mode)     | `.github/workflows/ci.yml`   |
| Docs build      | `zensical build --clean`                 | `.github/workflows/ci.yml`   |
| Security        | `pip-audit`                              | `.github/workflows/ci.yml`   |
| License (OSPO)  | `pip-licenses`, blocks AGPL/SSPL/GPL-3.0 | `.github/workflows/ci.yml`   |
| Dependencies    | Renovate (weekly, SHA-pinned Actions)    | `.github/renovate.json5`     |
